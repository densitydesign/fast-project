



function brand_hashtag(data) {
    var sx = $('#drawing-area').width();
    var sy = $('#drawing-area').height();

    var area = d3.select('#drawing-area') 
    var legend = area.append('div').attr('class', 'sankeylegend');
    var legend_ht = legend.append('span').html("");
    legend.append('span').html("&nbsp;&nbsp;&nbsp;");
    var legend_date = legend.append('span').html("");
    
    var svg = area.append('svg').attr('width', sx).attr('height', sy);

    var max_height, n_for_max;
    var rects = {};

    max_height = 0;
    n_for_max = 0;
    var days = []
    for (var day in data) {
        var sum = 0;
        var cnt = 0;
        var one_day = []
        var date = new Date(1000 * day)
        for (var ht in data[day]) {
            sum += data[day][ht];
            cnt++;
            one_day.push({ day: date.toDateString() + " - " + data[day][ht], ht: ht, value: data[day][ht]})
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

    function Rectangle(x0, y0, w, h, ht, val, date) {
        this.p = [
            { x: x0, y: y0 },
            { x: x0+w, y: y0 },
            { x: x0+w, y: y0+h },
            { x: x0, y:y0+h }
        ];
        this.o = this.p[0];
        this.s = { w: w, h: h};
        this.ht = ht;
        this.val = val;
        this.date = date;

        function highlight(obj, sts) {
            var r = d3.select(obj);
            var ht = r.attr("ht");
            var date = r.attr("date");

            if (sts) {
                legend_ht.html("#"+ht);
                legend_date.html(date);
            } else {
                legend_ht.html("");
                legend_date.html("");
            }

            for (var k in rects) {
                var className;
                
                if (!sts)
                    className = "sankey_norm";
                else if ( k == ht ) 
                    className = "sankey_on";
                else
                    className = "sankey_off";

                var path = rects[k];
                var n, j;
                n = path.length;
                
                for (j=0; j<n; j++) {
                    path[j].elt.attr("class", className);
                    path[j].text.attr("class", className);
                    if (path[j].link_out)
                        path[j].link_out.attr("class", className);
                }
            }
        }

        this.generate = function (svg) {
            this.elt = svg.append("rect");
            this.elt
                .attr("ht",ht)
                .attr("date", date)
                .attr("x",this.o.x).attr("y",this.o.y)
                .attr("width", this.s.w).attr("height", this.s.h)
                .attr("class", "sankey_norm");

            this.text = svg.append("text");
            var tx = this.o.x + this.s.w - 4;
            var ty = this.o.y + 4;
            
            this.text
                .text(val)
                .attr("date", date)
                .attr("ht",ht)
                .attr("x", tx)
                .attr("y", ty)
                .attr("transform", "rotate(270,"+tx+","+ty+")")
                .attr("text-anchor", "end")
                .attr("class","sankey_norm")
            ;

            this.elt
                .on("mouseover", function() { highlight(this, true); })
                .on("mouseout", function() { highlight(this, false); })
            ;
            this.text
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
                .attr("date","")
                .attr("class","sankey_norm")
                .attr("d", d);
            this.link_out
                .on("mouseover", function() { highlight(this, true); })
                .on("mouseout", function() { highlight(this, false); })
            ;
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

            rects[ht].push(new Rectangle(x0, y0, 20, v, days[jday][jht].ht, days[jday][jht].value, days[jday][jht].day));
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
