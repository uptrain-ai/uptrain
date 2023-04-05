import weightwatcher as ww
from uptrain.core.classes.monitors import AbstractCheck


class Finetune(AbstractCheck):

    def base_init(self, fw, check):
        self.optimizer = check["optimizer"]
        self.dataloader = check["dataloader"]
        self.layers = check["layers"]
        self.epochs = check.get("epochs", 1)
        self.device = check.get("device", "cpu")
        self.dashboard_name = "Finetuning Statistics"

    def base_check(self, inputs, outputs, gts=None, extra_args={}):
        model = inputs['model'][0]
        model.train()
        device = self.device
        num_all_points = 0
        for epoch in range(self.epochs):
            tr_loss = 0
            nb_tr_examples = 0
            for step, batch in enumerate(self.dataloader):
                batch = tuple(t.to(device) for t in batch)
                b_input_ids, b_input_mask, b_labels = batch
                b_labels = b_labels.to(device)
                b_input_ids = b_input_ids.to(device)
                b_input_mask = b_input_mask.to(device)
                
                self.optimizer.zero_grad()
                # Forward pass
                train_output = model(b_input_ids, 
                                    attention_mask = b_input_mask, 
                                        token_type_ids = None,
                                    labels = b_labels)
                # Backward pass
                train_output.loss.backward()
                self.optimizer.step()
                # Update tracking variables
                tr_loss += train_output.loss.item()
                nb_tr_examples += b_input_ids.size(0)
                num_all_points += b_input_ids.size(0)

                watcher = ww.WeightWatcher(model=model)
                a = watcher.analyze(layers=self.layers)
                a_list = a['alpha'].tolist()
                alpha_avg = sum(a_list)/len(a_list)

                self.log_handler.add_scalars(
                        "training_loss",
                        {"y_train_loss": tr_loss/nb_tr_examples},
                        num_all_points,
                        self.dashboard_name,
                    )
                
                self.log_handler.add_scalars(
                        "alpha_avg",
                        {"y_alpha_avg": alpha_avg},
                        num_all_points,
                        self.dashboard_name,
                    )