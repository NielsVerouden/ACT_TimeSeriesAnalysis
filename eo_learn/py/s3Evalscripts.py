# =============================================================================
# STEP 3: DEFINE EVALSCRIPT AND PROCESSING SCRIPT
# =============================================================================
# An evalscript (or "custom script") is a piece of Javascript code which defines 
# how the satellite data shall be processed by Sentinel Hub and what values the 
# service shall return. In this case, only VV and VH are returned and processed
# according to the card4l processing standards: 
# https://forum.sentinel-hub.com/t/eo-learn-tutorial-documentation-for-preprocessing-sentinel-1-data/4695

def inputEvalscripts():
    VV = """
        //VERSION=3
        function setup() {
          return {
            input: ["VV"],
            output: { 
                id:'VV', 
                bands: 1
                }
          }
        }
    function evaluatePixel(sample) {
        return [sample.VV];
    }    
    """
    VH = """
        //VERSION=3
        function setup() {
          return {
            input: ["VH"],
            output: { 
                id:'VH', 
                bands: 1
                }
          }
        }
    function evaluatePixel(sample) {
        return [sample.VH];
    }  
    """
    card4l_processing = {
        "backCoeff": "GAMMA0_TERRAIN",
        "orthorectify": True,
        "demInstance": "COPERNICUS",
        "downsampling": "BILINEAR",
        "upsampling": "BILINEAR",
        "speckleFilter": {
            "type": "LEE",
            "windowSizeX": 5,
            "windowSizeY": 5
            }
    }
    return VV, VH, card4l_processing
