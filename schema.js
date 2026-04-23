/**
 * schema.js — Schema definitions and validation for knowledge base entities.
 *
 * Provides runtime validation for atomic units, conversations, tags, and
 * relationships. Used by the API layer and import pipelines.
 */

/**
 * Valid unit types for atomic knowledge units.
 * @type {readonly string[]}
 */
export const UNIT_TYPES = Object.freeze([
  "insight",
  "code",
  "question",
  "reference",
  "decision",
]);

/**
 * Valid categories for classification.
 * @type {readonly string[]}
 */
export const CATEGORIES = Object.freeze([
  "programming",
  "writing",
  "research",
  "design",
  "general",
]);

/**
 * Validate an atomic unit object.
 * @param {object} unit - The unit to validate
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateUnit(unit) {
  const errors = [];

  if (!unit || typeof unit !== "object") {
    return { valid: false, errors: ["Unit must be an object"] };
  }
  if (!unit.id || typeof unit.id !== "string") {
    errors.push("id is required and must be a string");
  }
  if (!UNIT_TYPES.includes(unit.type)) {
    errors.push(`type must be one of: ${UNIT_TYPES.join(", ")}`);
  }
  if (!unit.title || typeof unit.title !== "string") {
    errors.push("title is required and must be a string");
  }
  if (unit.title && unit.title.length > 200) {
    errors.push("title must be 200 characters or fewer");
  }
  if (!unit.content || typeof unit.content !== "string") {
    errors.push("content is required and must be a string");
  }
  if (unit.category && !CATEGORIES.includes(unit.category)) {
    errors.push(`category must be one of: ${CATEGORIES.join(", ")}`);
  }
  if (unit.tags && !Array.isArray(unit.tags)) {
    errors.push("tags must be an array");
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate a tag object.
 * @param {object} tag
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateTag(tag) {
  const errors = [];
  if (!tag?.name || typeof tag.name !== "string") {
    errors.push("tag name is required");
  }
  if (tag.name && tag.name.length > 100) {
    errors.push("tag name must be 100 characters or fewer");
  }
  if (tag.name && !/^[a-z0-9][a-z0-9._-]*$/.test(tag.name)) {
    errors.push("tag name must be lowercase alphanumeric with dots, hyphens, underscores");
  }
  return { valid: errors.length === 0, errors };
}

/**
 * Validate a relationship object.
 * @param {object} rel
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateRelationship(rel) {
  const errors = [];
  if (!rel?.source_id) errors.push("source_id is required");
  if (!rel?.target_id) errors.push("target_id is required");
  if (rel?.source_id === rel?.target_id) errors.push("self-referencing relationships not allowed");
  if (rel?.strength != null && (rel.strength < 0 || rel.strength > 1)) {
    errors.push("strength must be between 0 and 1");
  }
  return { valid: errors.length === 0, errors };
}

export default {
  UNIT_TYPES,
  CATEGORIES,
  validateUnit,
  validateTag,
  validateRelationship,
};
