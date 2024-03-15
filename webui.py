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
                    getCorners().forEach((c, i) => ctx[i ? "lineTo" : "moveTo"](c[0] / 100 * ctx.canvas.width, c[1] / 100 * ctx.canvas.height));
                    ctx.closePath();
                    ctx.strokeStyle = 'cyan';
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
                
            </script>
            </body>
        </html>
    """.format(configStr=configStr)
