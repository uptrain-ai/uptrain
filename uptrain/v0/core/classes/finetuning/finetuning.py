try:
    import weightwatcher as ww
    WEIGHTWATCHER_PRESENT = True
except:
    WEIGHTWATCHER_PRESENT = False

try:
    import torch
    TORCH_PRESENT = True
except:
    TORCH_PRESENT = False


from uptrain.v0.core.classes.monitors import AbstractCheck


class Finetune(AbstractCheck):

    def base_init(self, fw, check):
        self.optimizer = check["optimizer"]
        self.train_dataloader = check["train_dataloader"]
        self.val_dataloader = check["val_dataloader"]
        self.layers = check["layers"]
        self.epochs = check.get("epochs", 1)
        self.device = check.get("device", "cpu")
        self.dashboard_name = "Finetuning Statistics"
        self.is_automated = check.get("is_automated", True)
        self.base_lr = check.get("base_lr", 2e-5)

    def getCustomLRParms(self, model):
        # TODO: Make 'post_bert' generic
        finetuned_names = [k for (k, v) in model.named_parameters() if 'post_bert' in k or 'classifier' in k]
        new_params= [v for k, v in model.named_parameters() if k in finetuned_names]
        pretrained = [v for k, v in model.named_parameters() if k not in finetuned_names]
        return new_params, pretrained

    def getTorchOptimizer(self, model, multipleFactor=1):
        if self.is_automated:
            new_params, pretrained = self.getCustomLRParms(model)
            optimizer_grouped_parameters = [
                {'params': new_params, 'lr': multipleFactor * self.base_lr},
                {'params': pretrained, 'lr': self.base_lr}
            ]
            optimizer = self.optimizer(optimizer_grouped_parameters)
            return optimizer
        else:
            return self.optimizer(model.parameters(), lr=self.base_lr)

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        model = inputs['model'][0]

        for name, param in model.named_parameters():
            if 'classifier' in name or 'post_bert' in name:
                print(name)
                param.requires_grad = True
            else:
                param.requires_grad = False


        optimizer = self.getTorchOptimizer(model)
        watcher = ww.WeightWatcher(model=model)
        model.train()

        device = self.device
        num_all_points = 0
        num_all_val_points = 0

        if not WEIGHTWATCHER_PRESENT:
            raise Exception("WeightWatcher is not installed. Please install it using 'pip install weightwatcher'")
        if not TORCH_PRESENT:
            raise Exception("PyTorch is not installed. Please install it using 'pip install torch'")
        for epoch in range(self.epochs):
            tr_loss = 0
            val_loss = 0
            nb_tr_examples, nb_tr_steps = 0, 0
            nb_val_examples, nb_val_steps = 0, 0
            for step, batch in enumerate(self.train_dataloader):

                a = watcher.analyze(layers=self.layers)
                a_list = a['alpha'].tolist()
                if self.is_automated:
                    if a_list[0] > 8:
                        optimizer = self.getTorchOptimizer(model, 5)

                alpha_avg = sum(a_list)/len(a_list)
                self.log_handler.add_scalars(
                    "alpha_avg",
                    {"y_alpha_avg": alpha_avg},
                    num_all_points,
                    self.dashboard_name,
                )

                batch = tuple(t.to(device) for t in batch)
                b_input_ids, b_input_mask, b_labels = batch
                b_labels = b_labels.to(device)
                b_input_ids = b_input_ids.to(device)
                b_input_mask = b_input_mask.to(device)
                
                optimizer.zero_grad()
                # Forward pass
                train_output = model(b_input_ids, 
                                    attention_mask = b_input_mask, 
                                        token_type_ids = None,
                                    labels = b_labels)
                # Backward pass
                train_output.loss.backward()
                optimizer.step()
                # Update tracking variables
                tr_loss += train_output.loss.item()
                nb_tr_examples += b_input_ids.size(0)
                num_all_points += b_input_ids.size(0)
                nb_tr_steps += 1

            self.log_handler.add_scalars(
                    "training_loss",
                    {"y_train_loss": tr_loss/nb_tr_steps},
                    num_all_points,
                    self.dashboard_name,
                )

            val_loss = 0
            nb_val_examples = 0
            for batch in self.val_dataloader:
                batch = tuple(t.to(device) for t in batch)
                b_input_ids, b_input_mask, b_labels = batch
                with torch.no_grad():
                    # Forward pass
                    eval_output = model(b_input_ids.to(device), 
                                        token_type_ids = None, 
                                        attention_mask = b_input_mask.to(device),
                                            labels = b_labels.to(device)
                                        )
                val_loss += eval_output.loss.item()
                nb_val_examples += b_input_ids.size(0)
                num_all_val_points += b_input_ids.size(0)
                nb_val_steps += 1

            self.log_handler.add_scalars(
                "validation_loss",
                {"y_val_loss": val_loss/nb_val_steps},
                num_all_points,
                self.dashboard_name,
            )
