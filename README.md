# Real-Time Audio Processing
Chaos theory + wavelets + denoising + other stuff
## Running
### Dependencies
Make sure you have the following installed properly:
- LiCoRICE

### Run Command
Run the file `run.sh`.
## Current State
- LiCoRICE works
- IDK how to process audio using it

# Note
- When outputting to `output.bin`:
  - `\x00` is transformed to `\x00\x01`
  - End of to-be-streamed packet is transformed to `\x00\x00`
