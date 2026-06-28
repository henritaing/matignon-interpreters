# Annotation Methodology

1. Data sources

Data Source: The dataset is sourced from Youtube.
Dataset Size: The dataset consists of 67 videos.
Sampling Method: Data is sampled using yt-dlp to extract videos.
Preprocessing Steps: Prior to annotation, the data is preprocessed by cropping the interpreter part of the image using Matignon-LSF cropping script.

2. Annotator Profile and Training

Annotator Demographics: The annotation team consists of 2 individuals (including me). The second annotator is a French Computer Science student. She isn't deaf and doesn't know sign language.

Training Process: The second annotator undergoes a 30-min training session where she reviews the annotation guidelines and has a demo during which I demonstrate the annotation process on 10 segments.

3. Gallery construction

A fast pass over all 67 videos is done to identify every distinct interpreter and create a frozen gallery with fixed IDs and fixed PNG references. This gallery is found in the folder called *data/Interpreter_gallery* which stays private to respect interpreters' privacy. After the pass, the gallery is reviewed for duplicate/merged IDs by the second annotator. The count of interpreters found in the gallery pass is compared against Halbout's reported count as a sanity check, discrepancies are examined.

4. Segment construction

To fix the video and transition segments, I fix all segment boundaries and transition windows across all 67 videos.

Transition starts when the interpreter goes out the frame and continue until the new interpreter is settled in the middle of frame with face visible.

5. Annotation Guidelines & Schema

Annotation Task: The goal of the task is to segment videos and assign to each segment an interpreter. 
Labeling Tool: The annotation process is conducted using a single Google Sheets "Annotation_results" that we'll later export as a CSV, *Annotation_results.csv*. Its columns are:
VideoID (List of IDs is provided in the Matignon-LSF_video_list.csv from Ouakrim), SegmentIndex (S_Number), Start of Segment (MM:SS), End of Segment (MM:SS), Transition Start (MM:SS), Transition End (MM:SS), Interpreter_Number_Annotator_A, Uncertainty_Flag_Interpreter_Annotator_A (Y/N), Interpreter_Number_Annotator_B, Uncertainty_Flag_Interpreter_Annotator_B (Y/N), Comments (Free text)

Using the frozen gallery and frozen segments, annotators assign labels in either Interpreter_Number_Annotator_A or Interpreter_Number_Annotator_B.

Edge Cases: Ambiguous cases are handled according to these specific rules:
- If there's a doubt on interpreter, each annotator writes 0 in their own column and raises their own uncertainty flag.
- If the face is not in the gallery, each annotator writes New_* in their own column and raises their own uncertainty flag. It is parked during annotation, adjudicated after the full pass, and splits are built only on resolved labels.

6. Quality Control

Annotation Overlap: To ensure reliability, 13 random videos (around 20% of the dataset) with a fixed seed are cross-annotated by 2 independent annotators using the same frozen interpreter gallery. 

Inter-Annotator Agreement (IAA): Agreement is measured using Cohen's Kappa, over the segments where both committed to a real ID.

Conflict Resolution: Disagreements are resolved through adjudication. If no consensus is reached, the segment is excluded and the number and identity of excluded segments are reported.

Validation strategy: TBD, must remain interpreter-disjoint from train and test for the canonical split

7. From annotation to splits (TBD)

Interpreter sets are disjoint because transitions and unresolved labels are removed before split construction.

The dataset is divided into multiple splits.
- Split 1: Training set with interpreter_1 (as many segments as possible), test set with 1 other interpreter
- Split 2: Training set with interpreter_1 (as many segments as possible), test with same interpreter, interpreter_1

