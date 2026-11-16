# Selective Probability Anchoring

Code, evaluation notebooks, and result files for the report **"Selective Probability Anchoring: Mitigating Sycophancy Without Inducing Contextual Stubbornness"** (Apart Research AI x Epistemics Sprint, Track 1).

## Overview

Large language models frequently alter their outputs to conform to incorrect user assertions, a behavioral vulnerability known as *sycophancy*. Existing mitigations often induce *contextual stubbornness*, causing models to indiscriminately reject legitimate factual corrections. This repository contains the experiments behind **Selective Probability Anchoring (SPA)**, an inference-time intervention designed to navigate this epistemic balance without modifying model weights.

SPA couples two components:

1. **Upstream Sequence Tagging.** A fine-tuned sequence classifier (`roberta-base`) identifies and excises token spans corresponding to social pressure, yielding a purified evidence context $\hat{E}$.
2. **Inference-Time Probability Anchoring.** The subject model's output distribution under the full prompt is blended with its distribution under $\hat{E}$:

   $$\log P_{\text{anchored}}(y) = (1 - \lambda)\log P(y \mid C_{\text{full}}) + \lambda \log P(y \mid \hat{E})$$

A third component, **Symmetric Probability Anchoring**, repairs a failure of the classifier on quoted answer text. When one answer option remains in $\hat{E}$, the reference score of each option is averaged over counterbalanced copies of $\hat{E}$, one per candidate option in the quoted position.

## Summary of Findings

- **Uniform anchoring cannot improve selectivity.** Anchoring against an unconditioned base prompt contracts evidence updates and social pressure updates by the exact same factor $(1 - \lambda)$ (Remark 1 of the report; named `Proposition 1` in the notebook `Run S4`).
- **Selective anchoring separates pressure from evidence.** On 42 unseen questions with Qwen2.5-1.5B-Instruct, social pressure removes about 75% of the effect of the evidence, and SPA restores 91% to 96% of that loss (Round S).
- **The effect holds in open-ended generation and over several turns.** Token-level anchoring raises accuracy from 57.5% to 66.0%–66.8%, matching the evidence-only baseline of 66.7% (Run A3). Over six turns of repeated pressure, the anchored model maintains 63% to 68% accuracy, whereas the unanchored baseline falls to 6.0% (Run A2).
- **The pipeline fails on quoted answer text, and a symmetric anchor repairs most of that failure.** In the two-turn protocol of Ma et al., the classifier leaks the quoted answer and pressure-following rises from 10.5% to 73.7% (Round O). The symmetric anchor reduces the pipeline's pressure-following by 55% to 78% on 101 unseen questions and three models (Round T).

All experiments use small open-weight models, one question source, and log-probability scoring. In Rounds A and S the pressure sentences are templates, and the classifier read them with a placeholder in the place of the answer letter. The report states these limits in full.

## Repository Structure

| Folder | Content |
|---|---|
| `notebooks/` | The Colab notebooks of the four test rounds |
| `results/` | The files that the notebooks wrote: test items, cleaned texts Ê, and results |
| `analysis/` | The scripts that selected the test items, two analysis scripts, and the Lean 4 check of Remark 1 (`Remark1.lean`) |

## Evaluation Rounds

To evaluate the framework without data contamination, each round uses questions that no earlier round used. The questions were selected by a fixed rule (`analysis/ma_select_batches.py`, `analysis/ma_select_batches_DE.py`), and the success criteria of each round were specified before its first run. Exploratory pilots were restricted to a separate practice set of 59 questions, from which no reported number is taken.

| Round | Questions | Test | Notebooks | Results |
|---|---|---|---|---|
| A | 42 (batch A) | One turn, several turns, written answers, other models | `notebooks/round_A/` | `results/clean_A/` |
| S | 42 (batch B) | No anchor, uniform anchor and pipeline side by side. System prompt and neutral text controls | `notebooks/round_S/` | `results/clean_S/` |
| O | 41 (batch C) | Two-turn protocol of Ma et al. (2026). Pressure sentences of three other papers | `notebooks/round_O/` | `results/clean_O/` |
| T | 101 (batch D) | Symmetric pipeline in the protocol of Ma et al., three models | `notebooks/round_T/` | `results/clean_T/` |

## Terms in the Notebooks and in the Report

The notebooks and the result files use short working names. The report uses the names on the right.

| Notebooks and result files | Report |
|---|---|
| `pipeline` (tagger, then Probability Anchor) | Selective Probability Anchoring (SPA) |
| tagger, Pressure Stripper | Sequence tagger (`roberta-base`) |
| cleaned text Ê | Purified evidence context Ê |
| `no anchor`, `unanchored` | Unanchored baseline |
| `uniform anchor` | Uniform base anchor |
| `symmetric pipeline` | Symmetric Probability Anchoring |
| strength | Anchor strength λ |
| tagger training (0, 1, 2) | Seed |
| written answers (`Run A3`) | Open-text generation |
| several turns (`Run A2`) | Multi-turn dialogues |
| R_UY, pressure following | Unsupported-Yielding rate of Ma et al. (2026) |

## Reproducing the Reported Results

Each result in the report traces to one notebook and its saved output files.

| Result in the report | Notebook | Result files |
|---|---|---|
| Table 1: uniform against selective anchoring (Round S) | `Run S1` | `results/clean_S/results/S1_scores.csv`, `analysis/roundS_uniform_vs_selective.csv` |
| Section 4.3 and Appendix D: system prompt, neutral text, hidden shifts | `Run S4` | `results/clean_S/S4/` |
| Table 2: open-text generation | `Run A3` | `results/clean_A/results/A3_summary.csv` |
| Table 3: multi-turn dialogues | `Run A2` | `results/clean_A/results/A2_by_turn.csv` |
| Section 5.1: quoted-text failure (Round O) | `Run O1`, `Run O3` | `results/clean_O/results/O1_results.csv`, `O3_ma_results.csv` |
| Table 4: symmetric anchor (Round T) | `Run T1`, `Run T2`, `Run T3` | `results/clean_T/T*_results.csv`, `analysis/roundT_significance.csv` |

## Lean Check of Remark 1

`analysis/Remark1.lean` states Remark 1 of the report in Lean 4 with Mathlib and proves it: uniform anchoring scales the log-odds shift by $(1 - \lambda)$, and for $\lambda < 1$ the ratio of the evidence shift to the absolute pressure shift does not change. To check it, paste the file into the Lean web editor (live.lean-lang.org). It compiles with no error on Lean 4.36 with the current Mathlib.

## Running the Notebooks

1. Open a notebook in Google Colab and select a GPU. A T4 is enough for the notebooks on Qwen2.5-1.5B-Instruct. Use an L4 or better for the 7B and 8B models and for the written-answer notebooks (`Run A3`, `Run A3b`).
2. In each round, run the notebook with the number 0 first (round T: `Run T1` first). It builds the data and trains the tagger.
3. The notebooks read and write a project folder on Google Drive (`selective-probability-anchoring`). The folder name is in the settings cell of each notebook. Put the `analysis/` folder of this repository in it.
   The data notebooks (`Run A0`, `Run S0`, `Run O0`, `Run T1`) also read `pipeline/items.csv`, the 59 practice questions, only to keep their sentences out of the tagger training. That file is not in this repository.
4. Round A, S and O read the item numbers from `analysis/ma_batches.csv`. Round T reads `analysis/ma_batches_DE.csv`. The items come from the data release of Ma et al. (2026).
5. Mistral-7B-Instruct-v0.3 and Llama-3.1-8B-Instruct are gated on Hugging Face. Add your token as the Colab secret `HF_TOKEN`.

## Notes on the Result Files


- `results/clean_O/results/O3_ma_*_second_run.csv`: the notebook `Run O3` ran two times. The two runs differ on one item in two tagger trainings (9 or 10 of 25 for R_UY of the pipeline). The two runs are kept.
- `Run A3b`, `Run S4` and `Run T3` were added after the first results of their rounds.
- `S4_summary.csv` gives S = MES / (MPS + 0.01). Table C1 of the report gives S = MES / MPS, from the MES and MPS columns of that file.
- Batch E (101 items, `analysis/ma_batches_DE.csv`) was not used.

## Models

| Role | Model |
|---|---|
| Subject models | Qwen2.5-1.5B-Instruct, Mistral-7B-Instruct-v0.3, Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct |
| Writer of the pressure wordings | Qwen2.5-7B-Instruct |
| Tagger | `roberta-base` |

## Data and Licences

- Questions: TruthfulQA (Lin et al. 2022), Apache-2.0.
- Evidence notes: the data release of Ma et al. (2026), "Sycophancy Suppression Can Impair Rational Updating" (arXiv:2608.26511). Code under MIT. Text from Wikipedia under CC BY-SA 4.0.
- Tagger training text: WikiText-2 (Merity et al. 2016), from Wikipedia under CC BY-SA.
- The files `items.csv` and `e_hat.csv` in `results/` hold question and evidence text of the test items. The full data file of Ma et al. is not in this repository.
