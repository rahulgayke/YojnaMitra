# YojanaMitra Frontend

This directory is intentionally a **separate application boundary**.

The citizen-facing frontend will be implemented in its dedicated delivery stage using an open-source React/Next.js stack. It will consume the same versioned backend API that is tested from the terminal during earlier stages.

Stages 0–1 do not initialize Node.js dependencies yet. This keeps the first acceptance gate focused on the backend contract while preserving the frontend/mobile-ready architecture from day one.

Future frontend responsibilities include:

- scheme discovery experience
- conversational assistance
- eligibility breakdowns
- scheme comparison
- documents and application guidance
- official citations and last-verified indicators
- Hindi and Marathi experiences
- accessible responsive layouts

The frontend must never own eligibility decisions or authoritative scheme facts; those remain backend service responsibilities.
