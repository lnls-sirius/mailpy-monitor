conn = new Mongo();

db = conn.getDB("mailpy-db");
db.getCollectionNames();

// ----- conditions ------
db.createCollection("conditions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "desc"],
      properties: {
        name: {
          bsonType: "string",
          description: "Required string type",
        },
        desc: {
          bsonType: "string",
          description: "Required string type",
        },
      },
    },
  },
});
db.conditions.createIndex({ name: 1 }, { unique: true });
db.conditions.insertMany([
  { name: "out of range", desc: "Must remain within the specified range." },
  { name: "superior than", desc: "Must remain superior than." },
  { name: "inferior than", desc: "Must remain inferior than." },
  { name: "increasing step", desc: "Each increasing step triggers an alarm." },
  { name: "decreasing step", desc: "Each decreasing step triggers an alarm." },
]);

// ----- groups ------
db.createCollection("groups", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "enabled"],
      properties: {
        name: {
          bsonType: "string",
          description: "Group name",
        },
        enabled: {
          bsonType: "bool",
          description: "Is group enabled",
        },
      },
    },
  },
});
db.groups.createIndex({ name: 1 }, { unique: true });

// ----- entries ------
db.createCollection("entries", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "alarm_values",
        "condition",
        "email_timeout",
        "emails",
        "group_name",
        "pvname",
        "subject",
        "unit",
        "warning_message",
      ],
      properties: {
        alarm_values: { bsonType: "string" },
        condition: { bsonType: "string" },
        email_timeout: { bsonType: "double" },
        emails: { bsonType: "string" },
        group_name: { bsonType: "string" },
        pvname: { bsonType: "string" },
        subject: { bsonType: "string" },
        unit: { bsonType: "string" },
        warning_message: { bsonType: "string" },
      },
    },
  },
});
db.createIndex(
  { pvname: 1, emails: 1, condition: 1, alarm_values: 1 },
  { unique: true }
);

// ----- Debug ------
db.getCollectionNames();
db.getCollectionInfos();
