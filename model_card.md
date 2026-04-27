# 🎧 Model Card: Music Recommender Simulation

## Model Name
**MatchYourVibe**

## Goal / Task
This system suggests 3 to 5 songs based on what a user wants to hear. It matches a user's taste profile (genre, mood, and energy) to the songs in our database to find the best fit.

## Data Used
The dataset is very small. It only has 17 songs. Each song has acoustic features (like energy and tempo) and text tags (like genre and mood). It does not include lyrics or user listening history. The data mostly covers extreme ends, like very high-energy pop or very quiet classical music.

## Algorithm Summary
We use a simple math formula to score each song. 
1. If the genre matches exactly, the song gets 1 point.
2. If the mood matches exactly, it gets 1 point.
3. The closer the song's energy is to the user's target energy, the more points it gets (up to 2 points max). 
The songs with the highest total scores win and get recommended first.

## Observed Behavior / Biases
The system struggles with contradictory requests. For example, if you ask for "Zero-Energy EDM", it gets confused and might give you sad classical music just to match the zero-energy rule. It also creates filter bubbles. Because it looks for exact word matches, asking for "lofi" means you will only ever get lofi songs, missing out on similar tracks.

## Evaluation Process
I tested standard profiles like "High-Energy Pop" and "Chill Lofi" to see if the normal math worked. Then, I tested trick profiles like "Aggressive Lullaby" to try and break the system. I read the terminal output to make sure the score explanations made sense. I also ran automated Python tests to prove my math changes were correct.

## Intended Use and Non-Intended Use
This system is meant for classroom exploration and learning about basic recommendation math. It is NOT for real users. It should not be used as a real product because the catalog is too small and the scoring is too simple to handle complex human tastes.

## Ideas for Improvement
1. **Use strict filters:** Force the system to only show hip-hop if you ask for hip-hop, instead of using points for genre.
2. **Use more song features:** Include tempo and danceability to make the matched songs smarter.
3. **Fuzzy matching:** Treat words like "chill", "relaxed", and "calm" as the same mood instead of requiring an exact match.

## Personal Reflection
My biggest learning moment was seeing how basic math can create major blind spots. Just adding points together breaks when user preferences contradict themselves. I was also very surprised by how a simple algorithm can still feel like a real app. For standard profiles like "Chill Lofi", checking just three basic features easily created a convincing playlist! 

Using AI tools helped me brainstorm those weird edge cases (like "Zero-Energy EDM") and quickly format text. However, I still had to double-check the logic when updating the energy math to make sure the new scoring passed the tests and made mathematical sense. If I extended this project, I would try adding collaborative filtering (recommending based on what similar users like) so the system isn't forced to rely entirely on strict tags.  
