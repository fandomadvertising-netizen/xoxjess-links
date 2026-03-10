#!/usr/bin/env python3
import json, os, shutil, html, sys

with open('models.json') as f:
    models = json.load(f)

# Filter by model name if --model flag is passed
# Usage: python build.py --model Ksana
model_filter = None
if '--model' in sys.argv:
    idx = sys.argv.index('--model')
    if idx + 1 < len(sys.argv):
        model_filter = sys.argv[idx + 1]
        models = [m for m in models if m['name'].lower() == model_filter.lower()]
        print(f"Filtering for model: {model_filter} ({len(models)} pages)")

out_dir = 'dist'

# Clean and create output directory
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

# Copy photos directory
if os.path.exists('photos'):
    shutil.copytree('photos', os.path.join(out_dir, 'photos'))

# Copy OF logo
if os.path.exists('of-logo-cropped.png'):
    shutil.copy2('of-logo-cropped.png', os.path.join(out_dir, 'of-logo.png'))


def generate_page(model):
    accent = model.get('theme', {}).get('accent', '#e91e8c')
    accent_hover = model.get('theme', {}).get('accentHover', '#ff2da3')
    name = html.escape(model['name'])
    tagline = html.escape(model['tagline'])
    profile_photo = model['profilePhoto']
    bg_photo = model['backgroundPhoto']
    of_link = model['ofLink']
    slug = model['slug']

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}</title>
  <meta name="description" content="{tagline}">
  <meta property="og:title" content="{name}">
  <meta property="og:description" content="{tagline}">
  <meta property="og:image" content="{bg_photo}">
  <meta property="og:type" content="website">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      min-height: 100vh;
      min-height: 100dvh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Inter', -apple-system, sans-serif;
      background: #0a0a0a;
      color: #fff;
      overflow-x: hidden;
    }}

    /* Background as a GPU-composited layer, completely isolated from DOM updates */
    .bg {{
      position: fixed;
      inset: 0;
      z-index: 0;
      background: url('{bg_photo}') center top / cover no-repeat;
      transform: translateZ(0);
      backface-visibility: hidden;
      pointer-events: none;
    }}

    @media (min-aspect-ratio: 1/1) {{
      .bg {{
        filter: blur(6px) brightness(0.9);
        transform: scale(1.05) translateZ(0);
      }}
    }}

    /* Dark gradient overlay */
    .bg-overlay {{
      position: fixed;
      inset: 0;
      background: linear-gradient(
        to top,
        rgba(0,0,0,0.95) 0%,
        rgba(0,0,0,0.7) 30%,
        rgba(0,0,0,0.2) 60%,
        transparent 100%
      );
      z-index: 1;
      transform: translateZ(0);
      pointer-events: none;
    }}

    /* Viewers counter - top of page */
    .viewers {{
      position: fixed;
      top: 0.75rem;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      background: rgba(0,0,0,0.6);
      backdrop-filter: blur(10px);
      padding: 0.25rem 0.65rem;
      border-radius: 20px;
      font-size: 0.6rem;
      color: rgba(255,255,255,0.7);
      animation: fadeUp 1s ease-out 0.5s both;
      contain: layout style;
    }}

    .viewers-dot {{
      width: 6px;
      height: 6px;
      background: #ef4444;
      border-radius: 50%;
      animation: blink 2s ease-in-out infinite;
    }}

    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
    }}

    .container {{
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1.5rem 3rem;
      max-width: 420px;
      width: 100%;
      animation: fadeUp 0.8s ease-out;
    }}

    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(30px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Profile photo circle */
    .photo-wrapper {{
      width: 120px;
      height: 120px;
      border-radius: 50%;
      padding: 3px;
      background: linear-gradient(135deg, {accent}, {accent_hover}, #fff);
      margin-bottom: 0.75rem;
      animation: shimmer 4s linear infinite;
      background-size: 300% 300%;
      flex-shrink: 0;
      position: relative;
    }}

    @keyframes shimmer {{
      0% {{ background-position: 0% 50%; }}
      50% {{ background-position: 100% 50%; }}
      100% {{ background-position: 0% 50%; }}
    }}

    .photo {{
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid #0a0a0a;
    }}

    /* Active Now green dot */
    .active-dot {{
      position: absolute;
      bottom: 6px;
      right: 6px;
      width: 18px;
      height: 18px;
      background: #22c55e;
      border-radius: 50%;
      border: 3px solid #0a0a0a;
      z-index: 3;
    }}

    .active-dot::after {{
      content: '';
      position: absolute;
      inset: -3px;
      border-radius: 50%;
      border: 2px solid #22c55e;
      animation: activePulse 2s ease-out infinite;
    }}

    @keyframes activePulse {{
      0% {{ transform: scale(1); opacity: 0.8; }}
      100% {{ transform: scale(1.8); opacity: 0; }}
    }}

    /* Name row with active status */
    .name-row {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.25rem;
    }}

    .name {{
      font-size: 1.75rem;
      font-weight: 700;
      text-shadow: 0 2px 15px rgba(0,0,0,0.7);
      margin-bottom: 0.3rem;
    }}

    .active-badge {{
      display: flex;
      align-items: center;
      gap: 0.3rem;
      background: rgba(34,197,94,0.15);
      border: 1px solid rgba(34,197,94,0.3);
      padding: 0.2rem 0.6rem;
      border-radius: 20px;
      font-size: 0.65rem;
      font-weight: 600;
      color: #22c55e;
      white-space: nowrap;
    }}

    .active-badge-dot {{
      width: 5px;
      height: 5px;
      background: #22c55e;
      border-radius: 50%;
    }}

    .tagline {{
      font-size: 0.95rem;
      color: rgba(255,255,255,0.7);
      text-align: center;
      margin-bottom: 1rem;
      line-height: 1.5;
      text-shadow: 0 1px 8px rgba(0,0,0,0.5);
    }}

    .hook-text {{
      font-size: 0.85rem;
      font-weight: 500;
      color: rgba(255,255,255,0.8);
      text-align: center;
      margin-bottom: 0.6rem;
      text-shadow: 0 2px 10px rgba(0,0,0,0.7);
    }}

    .hook-arrow {{
      display: inline-block;
      animation: bounce 1.5s ease-in-out infinite;
    }}

    @keyframes bounce {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(4px); }}
    }}

    /* Geo location badge */
    .geo {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
      margin-top: 0.5rem;
      font-size: 0.75rem;
      color: rgba(255,255,255,0.45);
    }}

    .geo-pin {{
      font-size: 0.8rem;
    }}

    /* Countdown timer */
    .countdown {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      background: rgba(239,68,68,0.12);
      border: 1px solid rgba(239,68,68,0.25);
      padding: 0.4rem 0.8rem;
      border-radius: 20px;
      font-size: 0.75rem;
      color: #fca5a5;
      margin-bottom: 1.25rem;
    }}

    .countdown-icon {{
      font-size: 0.85rem;
    }}

    .countdown-time {{
      font-weight: 700;
      color: #ef4444;
      font-variant-numeric: tabular-nums;
      display: inline-block;
      min-width: 4.5em;
    }}

    /* CTA Button */
    .cta {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      width: 100%;
      padding: 1rem 2rem;
      background: linear-gradient(135deg, {accent}, {accent_hover});
      color: #fff;
      text-decoration: none;
      border-radius: 50px;
      font-size: 1.1rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      transition: all 0.3s ease;
      box-shadow: 0 4px 25px {accent}66;
      position: relative;
      overflow: hidden;
    }}

    .cta:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 35px {accent}88;
    }}

    .cta:active {{
      transform: translateY(0);
    }}

    .cta::after {{
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: linear-gradient(
        to right,
        transparent 0%,
        rgba(255,255,255,0.15) 50%,
        transparent 100%
      );
      transform: rotate(30deg) translateX(-100%);
      animation: shine 3s ease-in-out infinite;
    }}

    @keyframes shine {{
      0%, 100% {{ transform: rotate(30deg) translateX(-100%); }}
      50% {{ transform: rotate(30deg) translateX(100%); }}
    }}

    .cta-icon-wrap {{
      width: 34px;
      height: 34px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      padding: 5px;
    }}

    .cta-icon {{
      width: 100%;
      height: 100%;
      object-fit: contain;
    }}

    .pulse-ring {{
      position: absolute;
      width: 100%;
      height: 100%;
      border-radius: 50px;
      border: 2px solid {accent};
      animation: pulse 2s ease-out infinite;
      pointer-events: none;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(1); opacity: 0.6; }}
      100% {{ transform: scale(1.15, 1.6); opacity: 0; }}
    }}

    .cta-wrapper {{
      position: relative;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    /* Spots left badge */
    .spots {{
      display: flex;
      align-items: center;
      gap: 0.3rem;
      margin-top: 0.75rem;
      font-size: 0.75rem;
      color: rgba(255,255,255,0.5);
    }}

    .spots-count {{
      color: #fbbf24;
      font-weight: 700;
    }}

    .badge {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      margin-top: 0.6rem;
      font-size: 0.8rem;
      color: rgba(255,255,255,0.5);
    }}

    .badge svg {{
      width: 14px;
      height: 14px;
      fill: {accent};
    }}

    /* Toast notification */
    .toast {{
      position: fixed;
      bottom: 1.5rem;
      left: 1rem;
      z-index: 20;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      background: rgba(0,0,0,0.8);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,0.1);
      padding: 0.6rem 1rem;
      border-radius: 12px;
      font-size: 0.75rem;
      color: rgba(255,255,255,0.9);
      transform: translateX(-120%);
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      max-width: 280px;
    }}

    .toast.show {{
      transform: translateX(0);
    }}

    .toast-avatar {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: linear-gradient(135deg, {accent}, {accent_hover});
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: 0.7rem;
    }}

    .toast-text {{
      line-height: 1.3;
    }}

    .toast-name {{
      font-weight: 600;
    }}

    .toast-time {{
      color: rgba(255,255,255,0.4);
      font-size: 0.65rem;
    }}

    /* Sticky CTA on mobile */
    .sticky-cta {{
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      z-index: 15;
      padding: 0.75rem 1rem;
      padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
      background: linear-gradient(to top, rgba(0,0,0,0.95), rgba(0,0,0,0.8), transparent);
    }}

    .sticky-cta .cta {{
      font-size: 1rem;
      padding: 0.85rem 1.5rem;
    }}

    @media (max-width: 768px) {{
      .sticky-cta.visible {{
        display: block;
      }}
    }}
  </style>
</head>
<body>
  <!-- Viewers counter -->
  <div class="viewers">
    <span class="viewers-dot"></span>
    <span><span id="viewerCount" style="display:inline-block;min-width:1.2em;text-align:center">0</span> people viewing right now</span>
  </div>

  <div class="bg"></div>
  <div class="bg-overlay"></div>

  <div class="container">
    <div class="photo-wrapper">
      <img class="photo" src="{profile_photo}" alt="{name}" loading="eager">
      <div class="active-dot"></div>
    </div>

    <div class="name-row">
      <h1 class="name">{name}</h1>
      <div class="active-badge">
        <span class="active-badge-dot"></span>
        Active now
      </div>
    </div>
    <p class="tagline">{tagline}</p>

    <!-- Countdown timer -->
    <div class="countdown">
      <span class="countdown-icon">&#128293;</span>
      <span>Free subscription ends in <span class="countdown-time" id="countdown">23:59:59</span></span>
    </div>

    <p class="hook-text">Looking for a new content partner <span class="hook-arrow">&#8595;</span></p>

    <div class="cta-wrapper">
      <div class="pulse-ring"></div>
      <a class="cta" href="/go/{slug}/" id="ctaButton" target="_blank" rel="noopener">
        <div class="cta-icon-wrap"><img class="cta-icon" src="/of-logo.png" alt="OnlyFans"></div>
        Chat with me now
      </a>
    </div>

    <div class="spots">
      <span>&#9888;&#65039;</span>
      <span>Only <span class="spots-count" id="spotsLeft">17</span> free spots remaining</span>
    </div>

    <div class="badge">
      <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>
      Verified Creator
    </div>

    <div class="geo" id="geoLocation">
      <span class="geo-pin">&#128205;</span>
      <span id="geoText">Locating...</span>
    </div>
  </div>

  <!-- Toast notification (slides in from bottom-left) -->
  <div class="toast" id="toast">
    <div class="toast-avatar">&#9829;</div>
    <div class="toast-text">
      <span class="toast-name" id="toastName">Someone</span> just subscribed
      <br><span class="toast-time" id="toastTime">2 min ago</span>
    </div>
  </div>

  <!-- Sticky CTA for mobile (appears on scroll) -->
  <div class="sticky-cta" id="stickyCta">
    <a class="cta" href="/go/{slug}/" target="_blank" rel="noopener">
      Chat with me now
    </a>
  </div>

  <script>
    /* Viewer count - random between 14-38, fluctuates */
    var vc = document.getElementById('viewerCount');
    var base = Math.floor(Math.random() * 15) + 18;
    vc.textContent = base;
    setInterval(function() {{
      base += Math.floor(Math.random() * 5) - 2;
      if (base < 12) base = 12 + Math.floor(Math.random() * 4);
      if (base > 42) base = 38 - Math.floor(Math.random() * 4);
      vc.textContent = base;
    }}, 4000 + Math.random() * 3000);

    /* Countdown timer - resets daily at midnight */
    function updateCountdown() {{
      var now = new Date();
      var end = new Date(now);
      end.setHours(23, 59, 59, 999);
      var diff = end - now;
      var h = String(Math.floor(diff / 3600000)).padStart(2, '0');
      var m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0');
      var s = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0');
      document.getElementById('countdown').textContent = h + ':' + m + ':' + s;
    }}
    updateCountdown();
    setInterval(updateCountdown, 1000);

    /* Toast notifications - fake subscriber alerts */
    var names = [
      'Alex', 'Jordan', 'Mike', 'Chris', 'Tyler', 'Jake', 'Ryan',
      'Brandon', 'Nick', 'Sam', 'Matt', 'David', 'James', 'Dan',
      'Kevin', 'Marcus', 'Derek', 'Lucas', 'Ethan', 'Noah'
    ];
    var locations = [
      'New York', 'Los Angeles', 'Miami', 'Houston', 'Chicago',
      'Phoenix', 'Dallas', 'Atlanta', 'Denver', 'San Diego',
      'Portland', 'Austin', 'Nashville', 'Las Vegas', 'Seattle'
    ];
    var times = ['just now', '1 min ago', '2 min ago', '3 min ago'];

    function showToast() {{
      var toast = document.getElementById('toast');
      var n = names[Math.floor(Math.random() * names.length)];
      var loc = locations[Math.floor(Math.random() * locations.length)];
      var t = times[Math.floor(Math.random() * times.length)];
      document.getElementById('toastName').textContent = n + ' from ' + loc;
      document.getElementById('toastTime').textContent = t;
      toast.classList.add('show');
      setTimeout(function() {{ toast.classList.remove('show'); }}, 4000);
    }}

    /* First toast after 5s, then every 15-30s */
    setTimeout(function() {{
      showToast();
      setInterval(showToast, 15000 + Math.random() * 15000);
    }}, 5000);

    /* Sticky CTA on mobile - show when user scrolls past main CTA */
    var mainCta = document.getElementById('ctaButton');
    var stickyCta = document.getElementById('stickyCta');
    if (window.innerWidth <= 768) {{
      var observer = new IntersectionObserver(function(entries) {{
        stickyCta.classList.toggle('visible', !entries[0].isIntersecting);
      }}, {{ threshold: 0 }});
      observer.observe(mainCta);
    }}

    /* Geo location from IP */
    fetch('https://ipapi.co/json/')
      .then(function(r) {{ return r.json(); }})
      .then(function(data) {{
        if (data.city) {{
          var miles = (Math.random() * 6 + 2).toFixed(1);
          document.getElementById('geoText').textContent = miles + ' miles away, located in ' + data.city;
        }} else {{
          document.getElementById('geoLocation').style.display = 'none';
        }}
      }})
      .catch(function() {{
        /* Fallback: try ip-api over http */
        fetch('http://ip-api.com/json/?fields=city')
          .then(function(r) {{ return r.json(); }})
          .then(function(data) {{
            if (data.city) {{
              var miles = (Math.random() * 6 + 2).toFixed(1);
              document.getElementById('geoText').textContent = miles + ' miles away, located in ' + data.city;
            }} else {{
              document.getElementById('geoLocation').style.display = 'none';
            }}
          }})
          .catch(function() {{
            document.getElementById('geoLocation').style.display = 'none';
          }});
      }});

  </script>
</body>
</html>'''


def generate_minimal_page(model):
    accent = model.get('theme', {}).get('accent', '#e91e8c')
    accent_hover = model.get('theme', {}).get('accentHover', '#ff2da3')
    name = html.escape(model['name'])
    tagline = html.escape(model['tagline'])
    profile_photo = model['profilePhoto']
    bg_photo = model['backgroundPhoto']
    of_link = model['ofLink']
    slug = model['slug']

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}</title>
  <meta name="description" content="{tagline}">
  <meta property="og:title" content="{name}">
  <meta property="og:description" content="{tagline}">
  <meta property="og:image" content="{bg_photo}">
  <meta property="og:type" content="website">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      min-height: 100vh;
      min-height: 100dvh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Inter', -apple-system, sans-serif;
      background: #0a0a0a;
      color: #fff;
      overflow-x: hidden;
    }}

    .bg {{
      position: fixed;
      inset: 0;
      z-index: 0;
      background: url('{bg_photo}') center top / cover no-repeat;
      transform: translateZ(0);
      backface-visibility: hidden;
      pointer-events: none;
    }}

    @media (min-aspect-ratio: 1/1) {{
      .bg {{
        filter: blur(6px) brightness(0.9);
        transform: scale(1.05) translateZ(0);
      }}
    }}

    .bg-overlay {{
      position: fixed;
      inset: 0;
      background: linear-gradient(
        to top,
        rgba(0,0,0,0.95) 0%,
        rgba(0,0,0,0.7) 30%,
        rgba(0,0,0,0.2) 60%,
        transparent 100%
      );
      z-index: 1;
      transform: translateZ(0);
      pointer-events: none;
    }}

    .container {{
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1.5rem 3rem;
      max-width: 420px;
      width: 100%;
      animation: fadeUp 0.8s ease-out;
    }}

    @keyframes fadeUp {{
      from {{ opacity: 0; transform: translateY(30px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .photo-wrapper {{
      width: 120px;
      height: 120px;
      border-radius: 50%;
      padding: 3px;
      background: linear-gradient(135deg, {accent}, {accent_hover}, #fff);
      margin-bottom: 0.75rem;
      animation: shimmer 4s linear infinite;
      background-size: 300% 300%;
      flex-shrink: 0;
      position: relative;
    }}

    @keyframes shimmer {{
      0% {{ background-position: 0% 50%; }}
      50% {{ background-position: 100% 50%; }}
      100% {{ background-position: 0% 50%; }}
    }}

    .photo {{
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
      border: 3px solid #0a0a0a;
    }}

    .active-dot {{
      position: absolute;
      bottom: 6px;
      right: 6px;
      width: 18px;
      height: 18px;
      background: #22c55e;
      border-radius: 50%;
      border: 3px solid #0a0a0a;
      z-index: 3;
    }}

    .name {{
      font-size: 1.75rem;
      font-weight: 700;
      text-shadow: 0 2px 15px rgba(0,0,0,0.7);
      margin-bottom: 0.3rem;
    }}

    .tagline {{
      font-size: 0.95rem;
      color: rgba(255,255,255,0.7);
      text-align: center;
      margin-bottom: 1.5rem;
      line-height: 1.5;
      text-shadow: 0 1px 8px rgba(0,0,0,0.5);
    }}

    .cta {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      width: 100%;
      padding: 1rem 2rem;
      background: linear-gradient(135deg, {accent}, {accent_hover});
      color: #fff;
      text-decoration: none;
      border-radius: 50px;
      font-size: 1.1rem;
      font-weight: 600;
      letter-spacing: 0.02em;
      transition: all 0.3s ease;
      box-shadow: 0 4px 25px {accent}66;
      position: relative;
      overflow: hidden;
    }}

    .cta:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 35px {accent}88;
    }}

    .cta:active {{
      transform: translateY(0);
    }}

    .cta::after {{
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: linear-gradient(
        to right,
        transparent 0%,
        rgba(255,255,255,0.15) 50%,
        transparent 100%
      );
      transform: rotate(30deg) translateX(-100%);
      animation: shine 3s ease-in-out infinite;
    }}

    @keyframes shine {{
      0%, 100% {{ transform: rotate(30deg) translateX(-100%); }}
      50% {{ transform: rotate(30deg) translateX(100%); }}
    }}

    .cta-icon-wrap {{
      width: 34px;
      height: 34px;
      background: #fff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      padding: 5px;
    }}

    .cta-icon {{
      width: 100%;
      height: 100%;
      object-fit: contain;
    }}

    .cta-wrapper {{
      position: relative;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .badge {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      margin-top: 0.75rem;
      font-size: 0.8rem;
      color: rgba(255,255,255,0.5);
    }}

    .badge svg {{
      width: 14px;
      height: 14px;
      fill: {accent};
    }}
  </style>
</head>
<body>
  <div class="bg"></div>
  <div class="bg-overlay"></div>

  <div class="container">
    <div class="photo-wrapper">
      <img class="photo" src="{profile_photo}" alt="{name}" loading="eager">
      <div class="active-dot"></div>
    </div>

    <h1 class="name">{name}</h1>
    <p class="tagline">{tagline}</p>

    <div class="cta-wrapper">
      <a class="cta" href="/go/{slug}/" id="ctaButton" target="_blank" rel="noopener">
        <div class="cta-icon-wrap"><img class="cta-icon" src="/of-logo.png" alt="OnlyFans"></div>
        Chat with me now
      </a>
    </div>

    <div class="badge">
      <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>
      Verified Creator
    </div>
  </div>
</body>
</html>'''


# Build each model page
for model in models:
    model_dir = os.path.join(out_dir, model['slug'])
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, 'index.html'), 'w') as f:
        if model.get('minimal'):
            f.write(generate_minimal_page(model))
        else:
            f.write(generate_page(model))
    variant = ' (minimal)' if model.get('minimal') else ''
    print(f"Built: /{model['slug']}/{variant}")

# Build redirect pages for CTA click tracking
for model in models:
    go_dir = os.path.join(out_dir, 'go', model['slug'])
    os.makedirs(go_dir, exist_ok=True)
    of_link = model['ofLink']
    redirect_page = f'''<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>Redirecting...</title>
</head><body>
<script>
// Small delay so Cloudflare Analytics beacon can fire before redirect
setTimeout(function() {{ window.location.replace("{of_link}"); }}, 150);
</script>
</body></html>'''
    with open(os.path.join(go_dir, 'index.html'), 'w') as f:
        f.write(redirect_page)
    print(f"Built: /go/{model['slug']}/")

# Root index (remove in production if you don't want a directory listing)
index_links = '\n    '.join(
    f'<li><a href="/{m["slug"]}/">{html.escape(m["name"])}</a></li>' for m in models
)
root_index = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Models</title>
<style>body{{font-family:sans-serif;background:#0a0a0a;color:#fff;padding:2rem}}a{{color:#e91e8c}}ul{{list-style:none;padding:0}}li{{margin:0.5rem 0}}</style>
</head><body><h1>Models</h1><ul>{index_links}</ul></body></html>'''

with open(os.path.join(out_dir, 'index.html'), 'w') as f:
    f.write(root_index)

print(f"\nDone! {len(models)} pages built in ./dist/")
