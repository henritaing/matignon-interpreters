# 24.05.2026

Decisions
- Scope confirmed: 67 videos of Matignon-LSF, not the wider live YouTube series
- Goal of the project: extending Artiaga to interpreted LSF + interpreter ID on Matignon-LSF
  - Methodological contribution: showing whether signer-dependence bias applies to interpreted SL.
  - Dataset contribution: producing interpreter labels and interpreter-disjoint splits for Matignon-LSF.
- Second annotator: sister, with sample-based IAA, kappa as metric
- Reached out on LinkedIn to Julie Lascar (Github owner) & Yanis Ouakrim (PhD)

Tech
- Tooling: uv + venv + VS Code, Python 3.11, repo created and pushed
- Folder structure created
- Environment set up

Research
- Re-read all the relevant references (/refs)
- 20 videos watched, 2 transitions/video typical, white-frame transitions with signer going out of frame
- Each signer / signer stay from 7 to 12 min
- Matignon-LSF video list isn't clear and script is outdated. After refactoring, with start date being July 2020 and end date being February 2024, I got more than 100 videos verifying the criteria "Conseil des ministres"
- Ortolang access issue: page blank, dataset may not be publicly released yet

What I learned
- Considered expanding scope but we don't want to build a new corpus, we want to layer a new label on an existing benchmark
- Convolutional neural network: a small filter (e.g., 3 weights) slides across the input. Each output neuron sees only a local window of the input, not all of it. The same weights are reused at every position. This gives translation invariance and far fewer parameters.
- Dense neural network, every neuron in layer N+1 receives input from every neuron in layer N.
- Temporal convolutional network (TCN): same idea but the convolution slides over time instead of space. Useful for sequences. A 1D convolution with kernel size 5 over a video means each output frame "sees" 5 surrounding frames.
- I3D = Inflated 3D ConvNet, a video model originally trained on Kinetics (action recognition), then in this case fine-tuned/pretrained on BSL-1K (a sign language dataset).
You feed it a short clip (typically 16 or 64 frames) and it outputs a fixed-size vector (1024-d typically) that summarizes the visual content of that clip. It's a learned representation — the model has seen millions of frames and learned what features distinguish different actions/signs. The vector itself isn't human-interpretable; it's just numbers that downstream models can use.
Why pre-extract them: running I3D on a 30-minute video is expensive. If you extract features once and save them, downstream models (translation, classification, your interpreter classifier eventually) train much faster.
- Why a transformer might be preferred over TCN for temporal localization: transformers can model long-range dependencies directly

Next steps:
- Email to Ouakrim/Braffort drafted, pending send Monday morning
- Annotation tool to be decided between ELAN and VIA
- Write annotation methodology