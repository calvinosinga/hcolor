
from hydrotools.interface import interface as iface_run


xtf = ['gr_dust']
shf = ['gr_normal', 'SubhaloPos', 'SubhaloVel', 'SubhaloMassType']
# fields from all of the particles
ptf = ['Coordinates','Velocities', 'Masses']
iface_run.extractGalaxyData(sim='tng75', snap_idx=99, paranoid=True, output_path='/lustre/cosinga/HI-color/results/', 
            file_suffix='_all_test', output_compression='gzip',catxt_get=True, catxt_fields=xtf, catsh_get=True, catsh_fields=shf,
            ptlstr_get=True, ptlstr_fields=ptf, num_processes = 20, randomize_order=True)

