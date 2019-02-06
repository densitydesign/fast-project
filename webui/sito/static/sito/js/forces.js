

function V2D(dx,dy) {
    this.dx = dx;
    this.dy = dy;

    this.toString = function() {
        return "V2D("+this.dx.toFixed(3).toString()+","+this.dy.toFixed(3).toString()+")";
    }
    this.add = function (that) {
        this.dx+=that.dx;
        this.dy+=that.dy;
    }
    this.scale = function (k) {
        var ret;
        ret = new V2D(k*this.dx, k*this.dy);
        return ret;
    }
    this.mod = function() {
        return Math.sqrt(this.dx*this.dx + this.dy*this.dy);
    }

    return this;
}

function P2D(x,y) {
    this.x = x;
    this.y = y;

    this.toString = function() {
        return "P2D("+this.x.toFixed(3).toString()+","+this.y.toFixed(3).toString()+")";
    }

    this.to = function(that) {
        var ret;

        ret = new V2D(this.x-that.x, this.y-that.y);
        return ret;
    }

    this.apply = function(v, minx, miny, maxx, maxy) {
        p = new P2D(this.x + v.dx, this.y + v.dy);
        if (p.x<minx)
            p.x = minx;
        if (p.x>maxx)
            p.x = maxx;
        if (p.y<miny)
            p.y = miny;
        if (p.y>maxy)
            p.y = maxy;
        return p;
    }

    return this;
}

function Spring(n1, n2, l, k, d) {
    this.n1 = n1;
    this.n2 = n2;
    this.target_len = l;
    this.k = k;
    this.d = d;

    this._l = function() {
        // var min = this.n1.size + this.n2.size;
        var v = this.n1.position.to(this.n2.position);
        // var ret = v.mod() - min;

        // if (ret < 0)
        //     ret = 0;

        return v.mod();
    }

    this.curr_len = this._l();
    this.last_len = this.curr_len;

    this.target = function(l) {
        this.target_len = l;
    }

    this.n1_n2 = function() {
        return this.n1.position.to(this.n2.position);
    }

    this.n2_n1 = function() {
        return this.n2.position.to(this.n1.position);
    }

    this.F = function () {
        var v,x;
        var ret;

        v = this.last_len - this.curr_len;
        x = this.target_len - this.curr_len;
        
        ret = -this.k*x-this.d*v;
        return ret;
    }

    this.tick = function () {
        this.last_len = this.curr_len;
        this.curr_len = this._l();
    }

    this.toString = function() {
        return "Spring("+this.n1.toString()+"->"+this.n2.toString()+" - |"+this.target_len.toString()+"| "+this.curr_len.toFixed(3).toString()+
            " "+(this.curr_len/this.target_len*100).toFixed(3)+"%)";
    }

    this.force = function() {
        return this.curr_len.toFixed(3).toString()+" "+(this.curr_len/this.target_len*100).toFixed(3)+"%";
    }

    this.add = function(svg) {
        this.elt = svg.append("line");
        this.elt
            .attr({ "x1": this.n1.position.x,
                    "y1": this.n1.position.y,
                    "x2": this.n2.position.x,
                    "y2": this.n2.position.y,
                    "style": "stroke:rgb(0,0,0);stroke-width:1"
                  })
        ;
    }

    return this;
}

function Node(name, size, color, description) {
    this.position = new P2D(0,0);
    this.name = name;
    this.size = size;
    this.force = new V2D(0,0);
    this.color = color;
    this.description = description;

    this.place = function(x,y) {
        this.position = new P2D(x,y);
    }

    this.no_force = function() {
        this.force = new V2D(0,0);
    }

    this.link = function(that) {
        return new Spring(this, that, 50, 0.3, 0.2);
    }

    this.toString = function() {
        return "Node "+this.name+ " @" + this.position.toString() + " →"+ this.force.toString();
    }

    this.add = function(svg) {
        this.elt = svg.append("circle");
        this.elt
            .attr("cx", this.position.x)
            .attr("cy", this.position.y)
            .attr("r", this.size/2)
            .attr("fill", this.color)
        ;
        this.label = svg.append("text");
        this.label
            .attr("x", this.position.x)
            .attr("y", this.position.y)
            .attr("text-anchor","middle")
        ;
        this.label.text(this.name);
    }
    
    return this;
}


function Net(nodes, arcs, width, height) {

    this.width = width;
    this.height = height;
    this.nodes = nodes;

    function rnd(min,max) {
        return Math.floor(Math.random() * (max-min+1) + min);
    }

    for (var n in this.nodes) {
        var origin, x1, y1, x, y;

        origin = this.nodes[n].size;
        x1 = this.width - origin;
        y1 = this.height - origin;
        x = rnd(origin,x1);
        y = rnd(origin,y1);

        this.nodes[n].place(x,y);
    }
    
    this.arcs = [];
    this.narcs = arcs.length;
    var j1;
    for (j1=0; j1<this.narcs; j1++) {
        this.arcs.push(new Spring(this.nodes[arcs[j1][0]], this.nodes[arcs[j1][1]], 200, 0.3, 0.2));
    }


    this._tick = function() {
        // reset forces
        for (var n in this.nodes)
            this.nodes[n].no_force();
        // calc spring
        for (var j1=0; j1<this.narcs; j1++) {
            var a,f;

            a = this.arcs[j1];
            a.tick();
            f = a.F();
            a.n1.force.add(a.n2_n1().scale(f));
            a.n2.force.add(a.n1_n2().scale(f));
        }
        // apply forces
        for (var n in this.nodes) {
            //console.log("Net.tick: " + n + " F=" + this.nodes[n].force.toString());
            this.nodes[n].position = this.nodes[n].position.apply(this.nodes[n].force.scale(0.002),
                                                                  this.nodes[n].size, this.nodes[n].size,
                                                                  this.width-this.nodes[n].size,
                                                                  this.height-this.nodes[n].size);
        }
    }

    this.random_place = function() {
        for (var j1=0; j1<20; j1++)
            this._tick();
    }

    this.dump = function(label) {
        console.log("==================== TICK "+label+" ====================");
        for (var n in this.nodes)
            console.log(this.nodes[n].toString());
        for (var j1=0; j1<this.narcs; j1++)
            console.log(this.arcs[j1].force());
    }

    this.draw = function(elt) {
        var area = d3.select(elt);
        var svg = area.append('svg').attr('width',this.width).attr("height",this.height);

        for (var j1=0; j1<this.narcs; j1++)
            this.arcs[j1].add(svg);
        
        for (var n in this.nodes)
            this.nodes[n].add(svg);
        
            
    }
    
    return this;
}


