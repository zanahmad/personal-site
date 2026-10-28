# Course recording source

The Chapter 8 recording is stored as ordered 8 MiB binary parts because large HTTPS uploads repeatedly failed. These parts concatenate to the exact QA-approved MP4; they are not separately playable clips. The manifest records every part and the complete file SHA-256.

Run `sh scripts/build-course-media.sh && hugo` to build the site. The script reassembles the original bytes under `static/teaching/probability-statistics/videos/`, verifies the complete checksum, and stops the build on a mismatch. Netlify uses this command for production and previews. Source parts are outside `static` and are not deployed. The larger original master remains in the teaching media archive.
