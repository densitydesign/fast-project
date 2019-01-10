



function brand_hashtag(data) {
    var sx = $('#drawing-area').width();
    var sy = $('#drawing-area').height();
    var svg = d3.select('#drawing-area').append('svg').attr('width', sx).attr('height', sy);

    var max_height, n_for_max;
    var rects = {};


    max_height = 0;
    n_for_max = 0;
    var days = []
    for (var day in data) {
        var sum = 0;
        var cnt = 0;
        var one_day = []
        for (var ht in data[day]) {
            sum += data[day][ht];
            cnt++;
            one_day.push({ ht: ht, value: data[day][ht]})
        }
        one_day.sort(function (a,b) {
            if (Math.abs(a.value-b.value)<0.003) {
                if (a.ht<b.ht)
                    return -1;
                else if (a.ht>b.ht)
                    return 1;
                else
                    return 0;
            }
            if (a.value > b.value)
                return -1;
            return 1;
        });
        days.push(one_day);
        if (sum > max_height) {
            max_height = sum;
            n_for_max = cnt;
        }
    }

    function Rectangle(x0, y0, w, h, ht) {
        this.p = [
            { x: x0, y: y0 },
            { x: x0+w, y: y0 },
            { x: x0+w, y: y0+h },
            { x: x0, y:y0+h }
        ];
        this.o = this.p[0];
        this.s = { w: w, h: h};
        this.ht = ht;

        style_rect = ["fill:blue;stroke:black;stroke-width:1", "fill:red;stroke:black;stroke-width:1"];
        style_link = ["fill:black; fill-opacity:0.2", "fill:yellow; fill-opacity:0.7"];

        function highlight(obj, sts) {
            var sr, sl;

            if (sts) {
                sr = style_rect[1];
                sl = style_link[1];
            } else {
                sr = style_rect[0];
                sl = style_link[0];
            }

            var r = d3.select(obj);
            var ht = r.attr("ht");
            var path = rects[ht];
            var n, j;
            n = path.length;

            for (j=0; j<n; j++) {
                path[j].elt.attr("style", sr);
                if (path[j].link_out)
                    path[j].link_out.attr("style", sl);
            }
        }

        this.generate = function (svg) {
            this.elt = svg.append("rect");
            this.elt
                .attr("ht",ht)
                .attr("x",this.o.x).attr("y",this.o.y)
                .attr("width", this.s.w).attr("height", this.s.h)
                .attr("style", style_rect[0]);

            this.elt
                .on("mouseover", function() { highlight(this, true); })
                .on("mouseout", function() { highlight(this, false); })
            ;
        }

        this.link_out = null;
        this.link = function (svg, next) {
            function quad(p0, p1) {
                dx = p1.x - p0.x;
                dy = p1.y - p0.y;
                return [
                    p0,
                    { x: p0.x + (dx / 4), y: p0.y },
                    { x: p0.x + (dx / 2), y: p0.y + (dy / 2) },
                    { x: p0.x + (3 * dx / 4), y: p1.y },
                    p1
                ];
            }

            function to_text(p) {
                return p.x+" "+p.y;
            }

            k = quad(this.p[1], next.p[0]).concat(quad(next.p[3], this.p[2]));
            d = [ "M", to_text(k[0]),
                  "Q", to_text(k[1]), to_text(k[2]),
                  "Q", to_text(k[3]), to_text(k[4]),
                  "L", to_text(k[5]),
                  "Q", to_text(k[6]), to_text(k[7]),
                  "Q", to_text(k[8]), to_text(k[9]),
                  "Z" ].join(" ");
            this.link_out = svg.append("path");
            this.link_out
                .attr("ht", this.ht)
                .attr("style",style_link[0])
                .attr("d", d);
            this.link_out
                .on("mouseover", function() { highlight(this, true); })
                .on("mouseout", function() { highlight(this, false); })
            ;
        }

        this.linktop = function (svg, next) {
            function quad(p0, p1) {
                dx = p1.x - p0.x;
                dy = p1.y - p0.y;
                return [
                    p0,
                    { x: p0.x + (dx / 4), y: p0.y },
                    { x: p0.x + (dx / 2), y: p0.y + (dy / 2) },
                    { x: p0.x + (3 * dx / 4), y: p1.y },
                    p1
                ];
            }

            function to_text(p) {
                return p.x+" "+p.y;
            }

            k = quad(this.p[1], next.p[0]).concat(quad(next.p[3], this.p[2]));
            d = [ "M", to_text(k[0]),
                  "Q", to_text(k[1]), to_text(k[2]),
                  "Q", to_text(k[3]), to_text(k[4])
                ].join(" ");
            this.link_out = svg.append("path");
            this.link_out
                .attr("style","stroke:black; stroke-opacity:0.5; fill:none;")
                .attr("d", d);
        }
        return this;
    }

    // calc rects
    var n_days = days.length;
    var hstep = (sy - n_for_max*10) / n_days;
    var jday;
    for (jday = 0; jday < n_days; jday++) {
        var x0 = jday * sx / (n_days+1);
        var y0 = 0;
        var jht, nht;

        nht = days[jday].length;
        for (jht = 0; jht < nht; jht++) {
            var v,ht;

            v = sy / max_height * days[jday][jht].value;
            ht = days[jday][jht].ht;
            if (rects[ht] == undefined)
                rects[ht] = [];

            rects[ht].push(new Rectangle(x0, y0, 10, v, days[jday][jht].ht));
            y0+=v+10;
        }
    }

    // draw links
    for (var ht in rects) {
        var n,j;
        var path;

        path = rects[ht];
        n = path.length;
        for (j=0; j<n-1; j++) {
            path[j].link(svg, path[j+1]);
        }
    }

    // draw rects
    for (var ht in rects) {
        var n,j;
        var path;

        path = rects[ht];
        n = path.length;
        for (j=0; j<n; j++) {
            path[j].generate(svg);
        }
    }

}
