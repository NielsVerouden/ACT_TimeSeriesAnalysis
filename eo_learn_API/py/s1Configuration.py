# =============================================================================
# STEP 1: CONFIGURE SENTINELHUB SETTINGS
# =============================================================================
from sentinelhub import SHConfig

def configSentinelHub(CLIENT_ID, CLIENT_SECRET, INSTANCE_ID):
    config = SHConfig()
    
    if CLIENT_ID and CLIENT_SECRET and INSTANCE_ID:
        # An instance ID for Sentinel Hub service used for OGC requests.
        config.instance_id = INSTANCE_ID
        
        # User's OAuth client ID for Sentinel Hub service
        config.sh_client_id = CLIENT_ID
        
        # User's OAuth client secret for Sentinel Hub service
        config.sh_client_secret = CLIENT_SECRET
        config.save()
        
    if config.sh_client_id == "" or config.sh_client_secret == "" or config.instance_id == "":
    
        return "Warning! To use Sentinel Hub services, please provide the credentials (client ID and client secret)."

