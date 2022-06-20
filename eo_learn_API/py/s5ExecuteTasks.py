# =============================================================================
# STEP 5: RUN WORKFLOW
# =============================================================================
from eolearn.core import EOWorkflow, linearly_connect_tasks
import os

def executeWorkflow(time_interval, file_name, tasks, roi_bbox):
    # Creates a list of linearly linked nodes, suitable to construct an EOWorkflow.
    VV = tasks[0]
    VH = tasks[1]
    DEM = tasks[2]
    SAVE = tasks[3]
    OUTPUT = tasks[4]
    workflow_nodes = linearly_connect_tasks(VV, VH, DEM, SAVE, OUTPUT)
    
    # Verifying and executing workflows defined by inter-dependent EONodes.
    workflow = EOWorkflow(workflow_nodes)

    # Execute all tasks defines in the workflow_nodes
    result = workflow.execute(
        {
            workflow_nodes[0]: {"bbox": roi_bbox, "time_interval": time_interval},
            workflow_nodes[-2]: {"eopatch_folder": 'workflow'},
        }
    )
    path = os.path.join('data/', file_name)

    # write output to eopatch variable
    eopatch = result.outputs[path]
    
    return eopatch