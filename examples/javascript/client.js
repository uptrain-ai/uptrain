const axios = require("axios");

/** Specify the field in each data row that map to question/response/context */
class DataSchema {
  constructor(data = {}) {
    this.id_ = data.id_ || "id";
    this.question = data.question || "question";
    this.response = data.response || "response";
    this.context = data.context || "context";
    this.ground_truth = data.ground_truth || "ground_truth";
  }
}

/** List of evaluations that you can evaluate the data on */
const Evals = {
  CONTEXT_RELEVANCE: "context_relevance",
  FACTUAL_ACCURACY: "factual_accuracy",
  RESPONSE_RELEVANCE: "response_relevance",
};

class APIClient {
  constructor(apiKey, serverUrl = "https://demo.uptrain.ai") {
    this.base_url = serverUrl.endsWith("/")
      ? serverUrl + "api/public"
      : serverUrl + "/api/public";
    this.client = axios.create({
      baseURL: this.base_url,
      timeout: 50000,
      headers: { "uptrain-access-token": apiKey },
    });

  }

  async checkAuth() {
    try {
      const response = await this.client.get("/auth");
      return response.data;
    } catch (error) {
      throw new Error(
        `Failed to connect to the Uptrain server at ${this.base_url}`
      );
    }
  }

  async log_and_evaluate(projectName, data, checks, schema = null, metadata = null) {
    const url = "/evaluate_v2";

    schema = schema ? new DataSchema(schema) : new DataSchema();
    metadata = metadata || {};

    const req_attrs = new Set();
    checks.forEach((m) => {
      if (m === Evals.CONTEXT_RELEVANCE) {
        req_attrs.add(schema.question);
        req_attrs.add(schema.context);
      } else if (m === Evals.FACTUAL_ACCURACY) {
        req_attrs.add(schema.response);
        req_attrs.add(schema.context);
      } else if (m === Evals.RESPONSE_RELEVANCE) {
        req_attrs.add(schema.question);
        req_attrs.add(schema.response);
      }
    });

    data.forEach((row, idx) => {
      const keys = Object.keys(row);
      req_attrs.forEach((attr) => {
        if (!keys.includes(attr)) {
          throw new Error(
            `Row ${idx} is missing required attributes for evaluation: ${[
              ...req_attrs,
            ].join(", ")}`
          );
        }
      });
    });

    const NUM_TRIES = 3,
      BATCH_SIZE = 50;
    let results = [];
    for (let i = 0; i < data.length; i += BATCH_SIZE) {
      let responseJson = null;
      for (let try_num = 0; try_num < NUM_TRIES; try_num++) {
        try {
          const response = await this.client.post(url, {
            data: data.slice(i, i + BATCH_SIZE),
            checks: checks,
            metadata: { project: projectName, ...metadata },
          });
          responseJson = response.data;
          break;
        } catch (error) {
          if (try_num === NUM_TRIES - 1) {
            throw error;
          }
        }
      }
      if (responseJson) {
        results = results.concat(responseJson);
      }
    }

    return results;
  }

  async download_project_results(projectName, fpath) {
    const url = `/evaluate_v2/${projectName}`;
    const response = await this.client.get(url);
    const fs = require("fs");
    fs.writeFileSync(fpath, response.data);
  }
}

module.exports = {
  APIClient,
  DataSchema,
  Evals,
};
