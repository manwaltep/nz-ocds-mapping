# Extensions

This directory will house formal JSON Schema definitions for each NZ extension proposed in the mapping.

Currently the extensions are documented in:
- `../mapping/ocds-nz-mapping-v0.4.xlsx` → **NZ Extensions** sheet (definition + Rule anchor + rationale)
- `../mapping/ocds-nz-mapping-v0.4.xlsx` → **OCDS Mapping** sheet (where each extension field lands in OCDS structure)

Once OCP Helpdesk has reviewed the v0.x mapping and we move toward formal extension registration, each extension will get its own subdirectory here following the [OCP extension template structure](https://github.com/open-contracting-extensions):

```
extensions/
├── README.md                                 ← this file
├── nz-treaty-of-waitangi-exception/
│   ├── README.md
│   ├── extension.json                        ← extension manifest
│   ├── release-schema.json                   ← JSON Schema additions
│   ├── release-schema.json (codelists)
│   └── docs/
├── nz-tender-coverage/
│   └── ...
└── ...
```

Until then, this directory is a placeholder.
