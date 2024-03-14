def webui_root(configStr):
    return """
        <html><head><title>dev studio</title></head>
        <body>
            <form method="post" action="/configure">
                <div>
                    <label for="head">Color of zero (min)</label>
                    <input type="color" name="colorZeroMin" value="#000000" />
                    <input type="text" disabled value="0, 0, 0">
                </div>
                <div>
                    <label for="head">Color of zero (max)</label>
                    <input type="color" name="colorZeroMax" value="#000000" />
                    <input type="text" disabled value="0, 0, 0">
                </div>
                <div>
                    <label for="head">Color of ball (min)</label>
                    <input type="color" name="colorBallMin" value="#000000" />
                    <input type="text" disabled value="0, 0, 0">
                </div>
                <div>
                    <label for="head">Color of ball (max)</label>
                    <input type="color" name="colorBallMax" value="#000000" />
                    <input type="text" disabled value="0, 0, 0">
                </div>
                <div>
                    <img src="/live-video" width="700" style="cursor:crosshair" />
                </div>
                <button>update</button>
            </form>
            <script>
                const config = JSON.parse(`{configStr}`);

                document.querySelector('input[name=colorZeroMin]').value = hsv2rgb(config.colors_hsv.zero[0]);
                document.querySelector('input[name=colorZeroMax]').value = hsv2rgb(config.colors_hsv.zero[1]);
                document.querySelector('input[name=colorBallMin]').value = hsv2rgb(config.colors_hsv.ball[0]);
                document.querySelector('input[name=colorBallMax]').value = hsv2rgb(config.colors_hsv.ball[1]);

                const img = document.querySelector('img');
                img.addEventListener('click', async e => {{
                    const x = e.clientX - img.offsetLeft;
                    const y = e.clientY - img.offsetTop;
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.canvas.width = img.width;
                    ctx.canvas.height = img.height;
                    ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
                    const p = ctx.getImageData(x, y, 1, 1).data;
                    document.querySelector("input").value = `#${{p[0].toString(16)}}${{p[1].toString(16)}}${{p[2].toString(16)}}`;
                }});

                document.querySelector('form').addEventListener('submit', event => {{
                    event.preventDefault();
                    config.colors_hsv = [[123,456,653],[132]];
                    config.corners = [
                        [1,2],[3,4]
                    ];
                    fetch('/configure', {{ method: 'post', body: JSON.stringify(config), headers: {{ 'Content-Type': 'application/json' }} }});
                }});

                // https://stackoverflow.com/a/54070620
                function rgb2hsv(rgb) {{
                    const r = parseInt(rgb.slice(1,3), 16) / 256;
                    const g = parseInt(rgb.slice(3,5), 16) / 256;
                    const b = parseInt(rgb.slice(5,7), 16) / 256;
                    const v = Math.max(r,g,b), c=v-Math.min(r,g,b);
                    const h = c && ((v==r) ? (g-b)/c : ((v==g) ? 2+(b-r)/c : 4+(r-g)/c));
                    return [60*(h<0?h+6:h) / 2, v&&c/v * 256, v * 256];
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
