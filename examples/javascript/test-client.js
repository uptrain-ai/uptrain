const { APIClient, Evals, DataSchema } = require("./client.js");

// Initialize the client
const apiKey = "up-********";
const serverUrl = "https://demo.uptrain.ai";
const client = new APIClient(apiKey, serverUrl);

// Check if client is authenticated
client
  .checkAuth()
  .then((response) => {
    console.log("Authentication status:", response);
  })
  .catch((error) => {
    console.error("Error during authentication:", error);
  });

// Define the data and other parameters you want to evaluate
const project = "Sample-Project";
const data = [
  {
    response:
      "The actress who played Lolita, Sue Lyon, was 14 at the time of filming.",
    question: "What was the age of Sue Lyon when she played Lolita?",
    context:
      "Lolita is a 1962 psychological comedy-drama film directed by Stanley Kubrick. The film follows Humbert Humbert, a middle-aged literature lecturer who becomes infatuated with Dolores Haze, a young adolescent girl. It stars Sue Lyon as the titular character.",
  },
  {
    response: "Shakespeare wrote 154 sonnets.",
    question: "How many sonnets did Shakespeare write?",
    context:
      "William Shakespeare was an English playwright and poet, widely regarded as the world's greatest dramatist. He is often called the Bard of Avon. His works consist of some 39 plays, 154 sonnets and a few other verses.",
  },
];

const metricsList = [Evals.CONTEXT_RELEVANCE, Evals.FACTUAL_ACCURACY];

// Evaluate
client
  .evaluate(project, data, metricsList)
  .then((results) => {
    console.log("Evaluation Results:", results);
  })
  .catch((error) => {
    console.error("Error during evaluation:", error);
  });
