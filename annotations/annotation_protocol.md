# Annotation Methodology

1. Data sources

Data Source: The dataset is sourced from Youtube.
Dataset Size: The dataset consists of 67 videos.
Sampling Method: Data is sampled using Youtube API to extract video, audio and subtitles.
Preprocessing Steps: Prior to annotation, the data is preprocessed by cropping the interpreter part of the image using Matignon-LSF cropping script.

2. Annotator Profile and Training

Annotator Demographics: The annotation team consists of 2 individuals (including me). The second annotator is a French Computer Science student. She isn't deaf and doesn't know sign language.

Training Process: The second annotator undergoes a 30-min training session where she reviews the annotation guidelines and has a demo during which I demonstrate the annotation process on 10 segments.

3. Gallery construction

A fast pass over all 67 videos is done to identify every distinct interpreter and create a frozen gallery with fixed IDs and fixed PNG references. This gallery is found in the folder called *data/Interpreter_gallery*. After the pass, the gallery is reviewed for duplicate/merged IDs by the second annotator. The count of interpreters found in the gallery pass is compared against Halbout's reported count as a sanity check, discrepancies are examined.

4. Annotation Guidelines & Schema

Annotation Task: The goal of the task is to segment videos and assign to each segment an interpreter. 
Labeling Tool: The annotation process is conducted using a single CSV called *Annotation_results.csv*.

Using the frozen gallery, annotators assign labels based on the following column names:
VideoID (List of IDs is provided in the Matignon-LSF_video_list.csv from Ouakrim), SegmentIndex (S_Number), Start of Segment (MM:SS), End of Segment (MM:SS), Uncertainty_Flag_Segment (Y/N), Interpreter_Number, Uncertainty_Flag_Interpreter (Y/N), Comments (Free text), Annotator (A/B for cross-annotation)

Edge Cases: Ambiguous cases are handled according to these specific rules:
- If there's a doubt on segment, raise the flag in the column "Uncertainty_Flag_Segment".
- If there's a doubt on interpreter, raise the flag in the column "Uncertainty_Flag_Interpreter" and put "0" in "Interpreter_Number"

5. Quality Control and Validation

Annotation Overlap: To ensure reliability, 13 random videos (around 20% of the dataset) with a fixed seed are cross-annotated by 2 independent annotators using the same frozen interpreter gallery.

Inter-Annotator Agreement (IAA): Agreement is measured using Cohen's Kappa. 

Conflict Resolution: Disagreements are resolved through adjudication. If no consensus is reached, the segment is excluded and the number and identity of excluded segments are reported.