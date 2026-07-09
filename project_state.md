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

Mental state: On one hand, excited, because I feel like I found a way to contribute, on the other, I hope that someone replies so I can move forward with it!

# 25.05.2026

30-min call with Ouakrim who kindly took the time to answer the questions I had.
1. Is there anyone already doing this project or something similar?
Not that he knows. He didn't know about the paper, Artiaga 2025. Maybe Julie Lascar who worked on Matignon-LSF, looked into it, but from what I found (Google Scholar), she worked and published on other topics.

2. Exact list of videos? Or Ortolang access?
Acquired exact list of videos used in Matignon-LSF but Ortolang access can't be given, at least by him.

3. Honest opinion on the project?
He looks optimistic, positive and excited to see what the end result will be. He's open to answering other questions if there's any.
For the last part, evaluate signer dependency, it will require fine-tuning of the chosen model on training dataset before evaluating it. We can then use for a Mediapipe model which is relatively lightweight to check if the poses are signer-dependant.
Also, he recommended using automatic segmentation and face recognition to label signers. Apparently one of the 2 Julie, developed a script to count the number of signers in the dataset they had. Since it hasn't been shared, I take it as it's either not maintained or experimental.

4. Visiting researcher status?
He mentioned asking relevant teams to become an associate researcher to get Ortolang and Jean Zay (French supercomputer) access.

5. CSV? ELAN? VIA? 
He only used a simple CSV format.

6. Other sources or documents?
- Dictasign LSF
- Julie Lascar and Julie Halbout papers to find if there's anything related to Matignon-LSF (haven't found anything on github.com/JulieLascar/Matignon-LSF, the repo was last updated 2 years ago except one folder, where a Python jupyter notebook was added to extend corpus from I understand)

Mental state: Was super stressed before the call, a bit intimated, but now I'm even more motivated to work on it! A litle tired though.

Decisions:
- Annotation tool: CSV

Next steps:
- Follow-up mail if more questions show (Already have some, model choice, mediapipe why? clarify fine-tuning, B Julie's script for automatic count of signers)
- Write annotation methodology

# 02.06.2026

Protocol v1 complete: data/annotation_protocol.md
- to avoid confirmation bias, we'll take the count of interpreters as a real output
- we'll do a full pass to build gallery, which will be frozen for cross-annotation and valid kappa

Decisions:
- Go with manual annotation, then automatic pipeline that we'll be able to test on the newly annotated dataset
- The gallery will be in the data folder which is ignored in .gitignore because we want to keep interpreters' privacy

Created the playlist with the list Ouakrim shared: https://www.youtube.com/watch?v=0hXvxmgHk_c&list=PLgtU_g_Bn-2Y1tvjm97zGzEZDhnpiM6Au

Checked again Lascar's Github, the crop part looks usable of the following script: https://github.com/JulieLascar/Matignon-LSF/blob/main/collecting_data/Downloading%20the%20videos%2C%20audio%2C%20and%20subtitles%20-%20Cropping%20the%20interpreter.ipynb
However, we'll have to find another solution for downloading the videos since pytube, yt-dl are not maintained anymore. Also, Youtube API doesn't allow it either since it's against their terms and conditions. 
It seems that yt-dlp works, see scripts/download.py

Next steps:
- Crop the videos
- Build the gallery in data/Interpreter_gallery for next week

Mental state: Realizing how rigorous you have to be in research.


# 09.06.2026

- Downloaded all the videos
- Used the cropping video algorith from Matignon-LSF, seems to work well. I ran it here and there, but it burns my laptop (it's an old laptop). I need to do it gradually. I added a loop just to avoid recropping videos already cropped, though it doesn't help with corrupted videos (mostly due to the fact that I stop the process when my pc gets too hot).

Next steps:
- Continue cropping the videos!

Mental state: Struggling to find time to run the cropping script and also lots of work so can't focus on the side-project.


# 12.06.2026

- Finally cropped everything!!! -> I thought I did, but actually many files were corrupted and some were incomplete due to the interruption of the script to charge the latop. After checking each video length and name, had to delete a few and now recropping them...
- Currently working on building the interpreter gallery, more difficult than what I expected. I found myself hesitating multiple times with the hairstyle and clothes change.

Next steps:
- Finish cropping
- Finish building the gallery in data/Interpreter_gallery

Mental state: Feeling like I'm making progress, but realizing that some videos were cut short or corrupted, urgh

## 27.06.2026

Just back from vacation, finally had time to complete the cropping!!! Even started building the gallery!


## 28.06.2026

Completed the gallery. I kid you not, I sometimes needed help from my brother. It's hard with hairstyle changes, lighting and the low resolution. Tracked my progress with a Google Sheets, with the following columns:
id	name	title	date	duration	Done?
The duration helped me verify if all videos were correctly downloaded and cropped.

Decisions:
- Write down results in Google Sheets before exporting it to CSV
- Segments are interpreter turns not movement bursts, presence anchor with a face-visible stop
- Transitions are recorded as windows and excluded before training
- The segments boundaries will be fixed in a first pass I'll make then labeled in another so kappa is computable
- Kappa will be over resolved IDs
- Added New_* as distinct uncertainty path, New_* parked then adjudicated before splitting

Next step:
- First pass for segmentation
- Annotation of the interpreters

## 01.07.2026

Finished segmentation and annotation of the interpreters, took me around 6h of focus (2h yesterday and 4h today) for the 37h of videos. It resulted in 242 segments. It was easier than expected but also longer than expected.

I didn't raise any uncertainty flag, neither used New_*. We'll see during the cross-annotation how it is.

Mental state: exhausted and tired eyes. There were also moments where I felt doubts on whether or not what I'm doing will be useful. My way to cope with this is to just accept the possibility of it being useless, but still a good learning experience.

## 08.07.2026

Experimenting with automation now that I've manually annotated the dataset.

This is the pipeline I have in mind for temporal video segmentation via blank (white/gray) handoff detection below.

For each video in the data/cropped_videos directory, I will:
1. Identify blank frames in the video (frames that are mostly white or gray). -> Drafted first version, blank.py
2. Return segments of the video between these blank frames and estimated transition times.
3. Save the tuple of timestamps as a csv file in the same directory as the video.

In order to have the best result, I will adjust cropping manually. Some of the cropped videos were a little off.

Next steps:
- Improve blank.py to get a transition time, ignore start and end peaks, adjust blankness threshold.

## 09.07.2026

Added comments to the scripts to describe their purposes and created randomsample.py to extract the random sample for cross-annotation.

Mental state:
- Tired from the heat and work and driving.