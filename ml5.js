/**
 * ml5.js — ML5.js integration for knowledge base intelligence features.
 *
 * Provides browser-compatible machine learning utilities for
 * text classification, sentiment analysis, and feature extraction
 * using pre-trained models via ml5.js.
 */

// ml5 is loaded as a global from CDN in browser contexts
// In Node.js contexts, this module provides a compatible shim.

const ML5_CDN = "https://unpkg.com/ml5@latest/dist/ml5.min.js";

/**
 * @typedef {Object} ClassificationResult
 * @property {string} label
 * @property {number} confidence
 */

/**
 * @typedef {Object} SentimentResult
 * @property {number} score - Sentiment score between 0 (negative) and 1 (positive)
 */

/**
 * Initialize ml5 sentiment analyzer.
 * @param {string} [model='movieReviews'] - Pre-trained model name
 * @returns {Promise<{predict: (text: string) => SentimentResult}>}
 */
export async function createSentimentAnalyzer(model = "movieReviews") {
  if (typeof window !== "undefined" && window.ml5) {
    return new Promise((resolve, reject) => {
      window.ml5.sentiment(model, (err, sentiment) => {
        if (err) return reject(err);
        resolve(sentiment);
      });
    });
  }
  // Node.js fallback: basic heuristic sentiment
  return {
    predict(text) {
      const positiveWords = ["good", "great", "excellent", "amazing", "helpful", "solved"];
      const negativeWords = ["bad", "wrong", "error", "fail", "broken", "terrible"];
      const words = text.toLowerCase().split(/\s+/);
      let score = 0.5;
      for (const w of words) {
        if (positiveWords.includes(w)) score += 0.05;
        if (negativeWords.includes(w)) score -= 0.05;
      }
      return { score: Math.max(0, Math.min(1, score)) };
    },
  };
}

/**
 * Text classifier for knowledge unit categorization.
 * @param {string} model - Model name or path
 * @param {Function} callback - Callback when model is ready
 */
export function createClassifier(model, callback) {
  if (typeof window !== "undefined" && window.ml5) {
    return window.ml5.textClassifier(model, callback);
  }
  // Node.js stub
  const classifier = {
    classify(text) {
      return Promise.resolve([
        { label: "general", confidence: 0.5 },
      ]);
    },
  };
  if (callback) callback(null, classifier);
  return classifier;
}

export default {
  createSentimentAnalyzer,
  createClassifier,
  CDN_URL: ML5_CDN,
};
