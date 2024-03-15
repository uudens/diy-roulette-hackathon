def webui_root(configStr):
    return """
        <html>
        <head>
            <title>dev studio</title>
            <style>
                .corner {{
                    cursor: pointer;
                    position: absolute;
                    border-radius: 50%;
                    background-color: cyan;
                    width: 15px;
                    height: 15px;
                    top: 0;
                    left: 0;
                    transform: translate(-50%, -50%);
                }}

                input[name=transform]:checked ~ .picker .corner,
                input[name=transform]:checked ~ .picker canvas {{
                    display: none;
                }}
            </style>
        </head>
        <body>
            <form method="post" action="/configure">
                <div style="display: flex; flex-direction: column;" class="colors">
                    <label><input type="range" min="0" max="179" name="colorZeroMinH" />color of zero, min, H <input /></label>
                    <label><input type="range" min="0" max="255" name="colorZeroMinS" />color of zero, min, S <input /></label>
                    <label><input type="range" min="0" max="255" name="colorZeroMinV" />color of zero, min, V <input /></label>
                    <label><input type="range" min="0" max="179" name="colorZeroMaxH" />color of zero, max, H <input /></label>
                    <label><input type="range" min="0" max="255" name="colorZeroMaxS" />color of zero, max, S <input /></label>
                    <label><input type="range" min="0" max="255" name="colorZeroMaxV" />color of zero, max, V <input /></label>
                    <label><input type="range" min="0" max="179" name="colorBallMinH" />color of ball, min, H <input /></label>
                    <label><input type="range" min="0" max="255" name="colorBallMinS" />color of ball, min, S <input /></label>
                    <label><input type="range" min="0" max="255" name="colorBallMinV" />color of ball, min, V <input /></label>
                    <label><input type="range" min="0" max="179" name="colorBallMaxH" />color of ball, max, H <input /></label>
                    <label><input type="range" min="0" max="255" name="colorBallMaxS" />color of ball, max, S <input /></label>
                    <label><input type="range" min="0" max="255" name="colorBallMaxV" />color of ball, max, V <input /></label>
                </div>
                <div>
                    <label>Color of zero (min)</label>
                    <input type="color" name="colorZeroMin" value="#000000" />
                    <input type="text" value="0, 0, 0">
                </div>
                <div>
                    <label>Color of zero (mid)</label>
                    <input type="color" name="colorZeroMid" value="#000000" />
                    <input type="text" value="0, 0, 0">
                </div>
                <div>
                    <label>Color of zero (max)</label>
                    <input type="color" name="colorZeroMax" value="#000000" />
                    <input type="text" value="0, 0, 0">
                </div>
                <div>
                    <label>Color of ball (min)</label>
                    <input type="color" name="colorBallMin" value="#000000" />
                    <input type="text" value="0, 0, 0">
                </div>
                <div>
                    <label>Color of ball (mid)</label>
                    <input type="color" name="colorBallMid" value="#000000" />
                    <input type="text" value="0, 0, 0">
                </div>
                <div>
                    <label>Color of ball (max)</label>
                    <input type="color" name="colorBallMax" value="#000000" />
                    <input type="text" value="0, 0, 0">
                </div>
                <label style="display: block"><input type="checkbox" name="live" />show live video</label>
                <label style="display: block"><input type="checkbox" name="chooseZero" />color picker picks color for zero</label>
                <input type="checkbox" name="transform" id="transform" /><label for="transform">show transformed video</label><br />
                <div class="picker" style="position: relative; display: inline-block; cursor: crosshair; user-select: none;">
                    <img src="/recorded-video" width="700" style="pointer-events: none;" />
                    <canvas style="position: absolute; top:0; left:0;"></canvas>
                    <div class="corner"></div>
                    <div class="corner"></div>
                    <div class="corner"></div>
                    <div class="corner"></div>
                </div>
                <button>update</button>
            </form>
            <script>
                const config = JSON.parse(`{configStr}`);

                document.querySelector('input[name=colorZeroMin]').value = hsv2rgb(config.colors_hsv.zero[0]);
                document.querySelector('input[name=colorZeroMin] + input').value = config.colors_hsv.zero[0];
                document.querySelector('input[name=colorZeroMax]').value = hsv2rgb(config.colors_hsv.zero[1]);
                document.querySelector('input[name=colorZeroMax] + input').value = config.colors_hsv.zero[1];
                document.querySelector('input[name=colorBallMin]').value = hsv2rgb(config.colors_hsv.ball[0]);
                document.querySelector('input[name=colorBallMin] + input').value = config.colors_hsv.ball[0];
                document.querySelector('input[name=colorBallMax]').value = hsv2rgb(config.colors_hsv.ball[1]);
                document.querySelector('input[name=colorBallMax] + input').value = config.colors_hsv.ball[1];
                document.querySelectorAll('.corner').forEach((el, i) => el.setAttribute("style", `top: ${{config.corners[i][1]}}%; left: ${{config.corners[i][0]}}%`));

                const img = document.querySelector('img');
                const canvas = document.querySelector('canvas');

                document.querySelectorAll('.colors input[name^=color]').forEach((el) => {{
                    el.addEventListener('change', () => {{
                        config.colors_hsv[el.name.includes('Zero') ? 'zero' : 'ball'][el.name.includes('min') ? 0 : 1][el.name.endsWith('H') ? 0 : (el.name.endsWith('S') ? 1 : 2)] = parseFloat(el.value);
                        el.parentElement.querySelector('input ~ input').value = el.value;
                    }});
                }});

                function updateSliders() {{
                    document.querySelectorAll('.colors input[name^=color]').forEach((el) => {{
                        el.value = config.colors_hsv[el.name.includes('Zero') ? 'zero' : 'ball'][el.name.includes('min') ? 0 : 1][el.name.endsWith('H') ? 0 : (el.name.endsWith('S') ? 1 : 2)];
                        el.parentElement.querySelector('input ~ input').value = el.value;
                    }});
                }}
                updateSliders();

                document.querySelector(".picker").addEventListener('click', async e => {{
                    const rect = img.getBoundingClientRect();
                    const x = e.clientX - rect.x;
                    const y = e.clientY - rect.y;
                    const ctx = document.createElement('canvas').getContext('2d');
                    ctx.canvas.width = img.width;
                    ctx.canvas.height = img.height;
                    ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
                    const p = ctx.getImageData(x, y, 1, 1).data;
                    const val = `#${{p[0].toString(16).padStart(2, "0")}}${{p[1].toString(16).padStart(2, "0")}}${{p[2].toString(16).padStart(2, "0")}}`;
                    const hsv = rgb2hsv(val);
                    const threshold = 0.1;
                    const hsvMin = [
                        //Math.round(((hsv[0] + 180) - 180 * threshold) % 180),
                        hsv[0],
                        Math.round(Math.max(0, hsv[1] - 256 * threshold)),
                        Math.round(Math.max(0, hsv[2] - 256 * threshold)),
                    ];
                    const hsvMax = [
                        //Math.round(((hsv[0] + 180) + 180 * threshold) % 180),
                        hsv[0],
                        Math.round(Math.max(0, hsv[1] + 256 * threshold)),
                        Math.round(Math.max(0, hsv[2] + 256 * threshold)),
                    ];
                    const key = document.querySelector('input[name=chooseZero]').checked ? 'zero' : 'ball';
                    config.colors_hsv[key][0][0] = hsvMin[0];
                    config.colors_hsv[key][0][1] = hsvMin[1];
                    config.colors_hsv[key][0][2] = hsvMin[2];
                    config.colors_hsv[key][1][0] = hsvMax[0];
                    config.colors_hsv[key][1][1] = hsvMax[1];
                    config.colors_hsv[key][1][2] = hsvMax[2];
                    updateSliders();
                    
                    el.parentElement.querySelector('input ~ input').value = el.value;
                    document.querySelector("input[name=colorZeroMid]").value = val;
                    document.querySelector("input[name=colorZeroMid] + input").value = rgb2hsv(val);
                    document.querySelector("input[name=colorZeroMin]").value = hsv2rgb(hsvMin);
                    document.querySelector("input[name=colorZeroMin] + input").value = hsvMin;
                    document.querySelector("input[name=colorZeroMax]").value = hsv2rgb(hsvMax);
                    document.querySelector("input[name=colorZeroMax] + input").value = hsvMax;
                }});

                let draggingEl = 0;
                document.body.addEventListener('mousemove', (e) => {{
                    if (draggingEl) {{
                        draggingEl.style.top = `${{100 * (e.clientY - draggingEl.parentElement.offsetTop) / draggingEl.parentElement.offsetHeight}}%`;
                        draggingEl.style.left = `${{100 * (e.clientX - draggingEl.parentElement.offsetLeft) / draggingEl.parentElement.offsetWidth}}%`;
                        drawQuadrilateral();
                    }}
                }});
                document.body.addEventListener('mouseup', () => {{ draggingEl = null; }})
                document.querySelectorAll('.corner').forEach(el => {{
                    el.addEventListener('mousedown', () => {{ draggingEl = el; }});
                }});

                function drawQuadrilateral() {{
                    const ctx = document.querySelector('canvas').getContext('2d');
                    ctx.canvas.width = img.width;
                    ctx.canvas.height = img.height;
                    ctx.beginPath();
                    const corners = getCorners();
                    ctx.strokeStyle = 'cyan';
                    corners.forEach((c, i) => ctx[i ? "lineTo" : "moveTo"](c[0] / 100 * ctx.canvas.width, c[1] / 100 * ctx.canvas.height));
                    ctx.closePath();
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(corners[0][0] / 100 * ctx.canvas.width, corners[0][1] / 100 * ctx.canvas.height);
                    ctx.lineTo(corners[2][0] / 100 * ctx.canvas.width, corners[2][1] / 100 * ctx.canvas.height);
                    ctx.moveTo(corners[1][0] / 100 * ctx.canvas.width, corners[1][1] / 100 * ctx.canvas.height);
                    ctx.lineTo(corners[3][0] / 100 * ctx.canvas.width, corners[3][1] / 100 * ctx.canvas.height);
                    ctx.stroke();
                }}
                img.addEventListener('load', drawQuadrilateral)

                function getCorners() {{
                    return [...document.querySelectorAll('.corner')].map(el => [Math.round(parseFloat(el.style.left)), Math.round(parseFloat(el.style.top))]);
                }}
                
                document.querySelector('form').addEventListener('submit', event => {{
                    event.preventDefault();
                    config.corners = getCorners();
                    config.transform = true;
                    fetch('/configure', {{ method: 'post', body: JSON.stringify(config), headers: {{ 'Content-Type': 'application/json' }} }});
                }});

                function showTransformedVideo(transform) {{
                    config.transform = transform;
                    fetch('/configure', {{ method: 'post', body: JSON.stringify(config), headers: {{ 'Content-Type': 'application/json' }} }});
                }}
                showTransformedVideo(false);
                document.querySelector('input[name=transform]').addEventListener('change', e => showTransformedVideo(e.target.checked));

                // https://stackoverflow.com/a/54070620
                function rgb2hsv(rgb) {{
                    const r = parseInt(rgb.slice(1,3), 16) / 256;
                    const g = parseInt(rgb.slice(3,5), 16) / 256;
                    const b = parseInt(rgb.slice(5,7), 16) / 256;
                    const v = Math.max(r,g,b), c=v-Math.min(r,g,b);
                    const h = c && ((v==r) ? (g-b)/c : ((v==g) ? 2+(b-r)/c : 4+(r-g)/c));
                    return [Math.floor(60*(h<0?h+6:h) / 2), Math.floor(v&&c/v * 256), Math.floor(v * 256)];
                }}

                // https://stackoverflow.com/a/54024653
                function hsv2rgb(opencvHSV) {{
                    const h = opencvHSV[0] * 2;
                    const s = opencvHSV[1] / 256;
                    const v = opencvHSV[2] / 256;
                    const f = (n,k=(n+h/60)%6) => v - v*s*Math.max( Math.min(k,4-k,1), 0);
                    return `#${{[Math.round(f(5) * 256).toString(16),Math.round(f(3) * 256).toString(16),Math.round(f(1) * 256).toString(16)].join("")}}`;
                }}

                document.querySelector("input[name=live]").addEventListener("change", (e) => {{
                    img.src = e.target.checked ? "/live-video" : "/recorded-video";
                }});
                
            </script>
            </body>
        </html>
    """.format(configStr=configStr)
