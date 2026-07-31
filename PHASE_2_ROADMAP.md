# Phase 2: Professional Grade (4-6 weeks)

## From Functional to Broadcast Quality

Phase 1 ✅ = Fully automated documentary production  
Phase 2 📋 = Emmy/Netflix/BBC-level production quality

---

## Phase 2 Enhancements

### 1. AI-Generated Scenes (Veo / Runway)
**Current:** Grok for still images, stock for footage  
**Phase 2:** Google Veo 2 or Runway for cinematic scene generation

- 30-second cinematic sequences where no footage exists
- Example: "Helicopter aerial view of South China Sea artificial islands"
- Cost: $0.15-0.20 per scene
- Quality: Professional, broadcast-ready

**Implementation:**
```python
# In ai_generator_agent.py
def generate_veo_scene(self, shot: Dict, prompt: str) -> Dict:
    """Generate cinematic scene using Google Veo 2"""
    response = veo_api.generate_video(
        prompt=prompt,
        duration=5,
        quality="high"
    )
    return response
```

---

### 2. Animated Maps (Google Earth Studio)
**Current:** Static map generation  
**Phase 2:** Cinematic map flyovers

- Zoom into location, pan across region
- Highlight points of interest
- Smooth camera movement
- Example: "Zoom into Nigeria, highlight Lagos, show location markers"

**Implementation:**
```python
# In timeline_builder_agent.py
def create_earth_studio_animation(self, location: str, duration: float) -> Dict:
    """Create cinematic map animation"""
    return {
        "type": "earth_studio_animation",
        "location": location,
        "duration": duration,
        "provider": "google_earth_studio"
    }
```

---

### 3. Satellite Imagery Integration
**Current:** Searches NASA API for static images  
**Phase 2:** Before/after satellite comparisons

- Automated download from NASA, Sentinel-2
- Split-screen: Year 1 vs Year 2
- Show change over time (construction, deforestation, etc.)
- Example: "Meta's Philippines facility construction 2019 → 2023"

**Providers:**
- NASA EOSDIS (free)
- Sentinel-2 (ESA, free)
- Google Earth Engine (free API)

---

### 4. Motion Graphics & Data Visualization
**Current:** Static infographics  
**Phase 2:** Animated data

- Animated bar charts (numbers growing)
- Animated pie charts (percentages appearing)
- Animated maps with data overlays
- Example: "Wage gap: $2 grows to $20 with animation"

**Implementation:**
```python
# New: graphics_animator_agent.py
def animate_statistic(self, value_start: float, value_end: float, label: str):
    """Animate number growth"""
    # Use Motion (open-source) or After Effects (premium)
    return animated_mp4
```

---

### 5. Professional Transitions (30+)
**Current:** Basic fade, cross-fade, wipe  
**Phase 2:** 30+ cinematic transitions

- Blur/pixelate dissolve
- Shape wipes (circle, diamond, polygon)
- 3D flips and rotations
- Morphing transitions
- Parallax effects

**Using:** FFmpeg + advanced filters, or AE plugins

---

### 6. Background Music & Sound Design
**Current:** Narration + audio from video  
**Phase 2:** Layered soundtrack

- Royalty-free music (Epidemic Sound, Artlist)
- Adaptive scoring (emotional lift at key moments)
- Sound effects (footsteps, papers shuffling, camera shutters)
- Ambient backgrounds (office ambience, street noise)

**Implementation:**
```python
# New: audio_designer_agent.py
def add_music_layer(self, emotion: str, duration: float) -> str:
    """Add adaptive background music"""
    tracks = {
        "critical": "dramatic_tension.mp3",
        "empathetic": "heartfelt_strings.mp3",
        "urgent": "fast_electronic.mp3",
        "hopeful": "uplifting_piano.mp3"
    }
    return mix_audio_layers(narration, tracks[emotion])
```

---

### 7. Enhanced Color Grading
**Current:** Simple desaturation/warming  
**Phase 2:** Professional LUTs (Look-Up Tables)

- Professional cinematography LUTs
- Per-scene color grading
- Consistent color palette
- Skin tone preservation

**Tools:** FFmpeg color grading, DaVinci Resolve (via FFmpeg export)

---

### 8. Add Second Agent: Audio Designer
**New agent:** audio_designer_agent.py

Responsibilities:
- Select music per emotional tone
- Mix layers (music + SFX + narration)
- Normalize audio levels
- Add spatial audio (surround sound)

---

## Tech Stack Addition (Phase 2)

| Component | Tool | Cost | Notes |
|-----------|------|------|-------|
| Cinematic video | Google Veo 2 | $0.15/scene | OR Runway ($0.10) |
| Map flyovers | Google Earth Studio | Free | Automated via API |
| Satellite imagery | NASA EOSDIS | Free | Automated download |
| Motion graphics | Motion (macOS) | $20 one-time | OR After Effects |
| Music/SFX | Epidemic Sound | $10/mo | OR Artlist ($15/mo) |
| Color grading | FFmpeg LUTs | Free | DaVinci Resolve export |
| Text-to-speech | ElevenLabs | $5 per video | (already in Phase 1) |

**Total additional cost:** ~$15-20 per video (vs $5-7 in Phase 1)

---

## Phase 2 Workflow (Enhanced)

```
Script
  ↓
[1] Research Agent (unchanged)
  ↓
[2] Script Analyzer (unchanged)
  ↓
[3] Visual Planner (enhanced: more sophisticated choices)
  ↓
[4] Asset Finder (add: NASA satellite, Google Earth)
  ↓
[5] AI Generator (add: Veo scenes, animated graphics)
  ↓
[6] Audio Designer ← NEW
    └─ Add music, SFX, layering
  ↓
[7] Timeline Builder (unchanged)
  ↓
[8] Graphics Animator ← NEW
    └─ Animate data, charts, text
  ↓
[9] FFmpeg Editor (enhanced: 30+ transitions, LUTs, spatial audio)
  ↓
[10] Quality Review (add: audio mix check, music sync check)
```

---

## Estimated Timeline

- **Week 1:** Veo/Runway integration + Google Earth Studio API
- **Week 2:** Animated graphics + data visualization
- **Week 3:** Music/SFX layer + audio designer agent
- **Week 4:** Professional color grading + LUTs
- **Week 5:** Testing, refinement, 2-3 test videos
- **Week 6:** Documentation, handoff

---

## Expected Quality Improvement

**Phase 1:** Professional documentary (BBC News level)  
**Phase 2:** Premium documentary (Netflix/HBO level)

Difference: Cinematic scenes, animated data, professional music, smooth transitions

---

## Phase 3: Self-Improving System (Future)

**Auto-critique agents:**
- Watch finished video
- Detect weak sections (boring shots, pacing issues, weak visuals)
- Auto-suggest improvements
- Re-edit and re-render
- Iterate until quality threshold met

**This is where system resembles professional documentary studio operations.**

---

## Phase 2 Priority Order

1. **Veo/Runway** (biggest visual impact)
2. **Animated maps** (geographic context teaching)
3. **Music + SFX** (emotional lift)
4. **30+ transitions** (professionalism)
5. **LUT color grading** (consistency)
6. **Motion graphics** (data visualization)

---

**Phase 2 Status:** Ready to plan implementation  
**Estimated effort:** 4-6 weeks  
**Cost impact:** +$10-15 per video  
**Quality jump:** ~50% closer to professional documentaries
