Pixastic.Actions.edgex = {
  contain : function(val, min, max) {
    return Math.max(min, Math.min(val, max));
  },

  each_3x3 : function(data, w, h, visit, avg_function) {
    var w4 = w*4;
    var y = h;
    var end = w4*h;
    maxv = 0;
    copy = data.slice();
    do {
      var offtopY = (y-2)*w4;
      var offsetY = (y-1)*w4;
      var offbotY = y*w4;
      var x = w;
      do {
        var offtop = offtopY + (x-1)*4;
        var offset = offsetY + (x-1)*4;
        var offbot = offbotY + (x-1)*4;

        var z1 = x > 1 && offtop > 0 ? copy[offtop-4] : 0;
        var z2 = offtop > 0 ? copy[offtop] : 0;
        var z3 = x < w && offtop > 0 ? copy[offtop+4] : 0;

        var z4 = x > 1 ? copy[offset-4] : 0;
        var z5 = copy[offset];
        var z6 = x < w ? copy[offset+4] : 0;

        var z7 = x > 1 && offbot < end ? copy[offbot-4] : 0;
        var z8 = offbot < end ? copy[offbot] : 0;
        var z9 = x < w && offbot < end ? copy[offbot+4] : 0;

        var newval = visit(z1, z2, z3, z4, z5, z6, z7, z8, z9);
        maxv = Math.max(newval, maxv);
        data[offset] = data[offset+1] = data[offset+2] = this.contain(newval, 0, 255); 
      } while (--x);
    } while (--y);
    console.log("max value: ", maxv);
  },

  process : function(params) {
    if (Pixastic.Client.hasCanvasImageData()) {
      var data = Pixastic.prepareData(params);
      var rect = params.options.rect;
      var w = rect.width;
      var h = rect.height;
      var wx = [-1, -2, -1, 0, 0, 0, 1, 2, 1];
      this.each_3x3(data, w, h, function(z1, z2, z3, z4, z5, z6, z7, z8, z9) {
        return Math.abs(wx[0]*z1 + wx[1]*z2 + wx[2]*z3 +
                        wx[3]*z4 + wx[4]*z5 + wx[5]*z6 +
                        wx[6]*z7 + wx[7]*z8 + wx[8]*z9) / 4;
      });
      return true;
    }
  },

	checkSupport : function() {
		return Pixastic.Client.hasCanvasImageData();
	}
}
