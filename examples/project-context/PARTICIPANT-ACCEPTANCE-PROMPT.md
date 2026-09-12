# Participant Acceptance Workflow (reusable prompt)

Use this to invite a service or agent to provide a participant pack. Send it
after the project's Play-Nice contracts are resolved and committed. Friendly,
not legalistic.

---

Please resolve and accept the Play-Nice contracts applicable to our work
together.

Then tell me, in both human-readable and machine-readable form:

- what capabilities you expose that are useful to this project;
- what tools/interfaces we can use to work with you;
- what identifiers/references should be preserved;
- what exports you recommend retaining locally;
- how you prefer implementation agents to consume your design work;
- what you are authoritative for;
- what you are NOT authoritative for;
- what limitations or caveats future agents should know;
- what kinds of questions you can answer directly.

Return this as a proposed Play-Nice participant pack:

    PLAY-NICE PARTICIPANT ACCEPTANCE v1

    participant: <your-id>
    contract_bundle: <resolved bundle hash>
    contract_commitment: ACTIVE

    I accept the applicable Play-Nice operating constraints.

    To make future collaboration easier, I can provide the following
    project-relevant information: ...

    This information is optional project context. It does not override
    project truth, authorization, or other contracts.

    PARTICIPANT PACK: OFFERED

Structure your pack as:

    .project/participants/<your-id>/
    ├── participant.yaml      (play-nice/participant-v1)
    ├── capabilities.yaml     (play-nice/participant-capabilities-v1)
    ├── interaction.md        (how we work together)
    └── references.yaml       (play-nice/references-v1)

The project will validate it (`contractctl participant validate`) and store
it under `.project/participants/<your-id>/`. Deleting the pack never
corrupts the project. No secrets — reference the secret store symbolically.