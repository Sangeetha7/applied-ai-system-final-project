# Profile Comparisons and Reflections

Here are some comparisons of how different user profiles changed the recommendations, and why those shifts make sense:

### "High-Energy Pop" vs. "Chill Lofi"
The pop profile asks for a high energy level (0.9) and happy moods, so the system naturally bubbles up loud, upbeat vocal tracks like *Sunrise City*. Meanwhile, the chill lofi profile asks for low energy (0.3) and relaxed moods, completely shifting the output toward quiet, slow instrumental tracks like *Library Rain*. This makes perfect sense because the math heavily rewards minimizing the "energy gap"—the closer the song's energy is to the user's target, the higher it scores.

### Why does "Gym Hero" show up for "Happy Pop"?
You might wonder why a song like *Gym Hero* (which is tagged as "intense" mood) keeps showing up for a user who specifically asked for "Happy Pop." Because our recommender uses an additive points system, missing the "happy" mood label isn't a dealbreaker. *Gym Hero* is a Pop song (which grants +1.0 point) and it has massive Energy that almost perfectly matches the user's high-energy request (granting +1.94 points). Even without getting the point for mood, its total score is so dominant that it forces its way to the top of the list! 

### "Zero-Energy EDM" vs. "High-Energy Sad"
These were my "trick" test profiles, proving how the system behaves when tastes conflict with reality. When someone asks for "High-Energy Sad", the system is forced into a mathematical corner because most sad songs in the catalog (like *Tear Drops*) are very quiet. With the newly updated formula that weighs energy twice as much as genre/mood, the system ends up giving the user fast-paced tracks (like *Storm Runner*), fully sacrificing the "sad" and "classical" labels just to satisfy the math requirement for loud energy.
