from hydrotools.interface import interface as iface_run

def extractParticles(num_processes = 32, sim = 'tng75', z = 0.0):

	# ---------------------------------------------------------------------------------------------
	# Set mass limits

	mass_selection_type = 'or'
	
	if sim in ['orig', 'tng75']:
		Mstar_min = 2E8
		Mgas_min = 2E8
	elif sim == 'tng205':
		Mstar_min = 5E10
		Mgas_min = 5E9
	elif sim == 'tng75-2':
		Mstar_min = 1.1E9
		Mgas_min = 1.1E9
	elif sim == 'tng75-3':
		Mstar_min = 9E9
		Mgas_min = 9E9
	else:
		raise Exception('Unknown sim, %s' % sim)
	
	# ---------------------------------------------------------------------------------------------
	# Set UV algorithm

	uv_propagate = True
	uv_from_local_sfr = False
	uv_sfr_local = 1E-3
	uv_escape_frac = 0.1

	# ---------------------------------------------------------------------------------------------
	# Particle output
	
	allptl_path = None
	if sim == 'tng75':
		allptl_path = '/lustre/cosinga/tng100/postprocessing/hih2'
	# elif sim == 'tng75-2':
	# 	allptl_path = '/n/hernquistfs3/IllustrisTNG/Runs/L75n910TNG/postprocessing/hih2'
	# elif sim == 'tng75-3':
	# 	allptl_path = '/n/hernquistfs3/IllustrisTNG/Runs/L75n455TNG/postprocessing/hih2'
	else:
		raise Exception('Sim not listed for allptl output.')
		
	# ---------------------------------------------------------------------------------------------
	# Extract
	
	# iface_run.extractGalaxyData(num_processes = num_processes,
	# 		sim = sim, snap_z = z,
	# 		mass_selection_type = mass_selection_type,
	# 		Mstar_min = Mstar_min, Mgas_min = Mgas_min, 
	# 		paranoid = True, verbose = False,
	# 		uv_from_local_sfr = uv_from_local_sfr, uv_sfr_local = uv_sfr_local, uv_propagate = uv_propagate, 
	# 		uv_escape_frac = uv_escape_frac, uv_ngrid = 128,
	# 		catsh_get = False, catgrp_get = False,
	# 		allptl_get = True, allptl_file_prefix = 'hih2_particles_',
	# 		allptl_path = allptl_path,
	# 		allptl_fields = ['ptlgas_f_mol_GK11', 'ptlgas_f_mol_GD14', 
	# 			'ptlgas_f_mol_K13', 'ptlgas_f_mol_S14', 'ptlgas_f_neutral_H'])

	iface_run.extractGalaxyData(num_processes = num_processes, sim = sim,
			mass_selection_type = mass_selection_type, 
			Mstar_min = Mstar_min, Mgas_min = Mgas_min,
			paranoid = True, verbose = False,
			catsh_get = False, catgrp_get = False,
			allptl_get = True, allptl_file_prefix = 'hih2_particles_',
			allptl_path = allptl_path,
			allptl_fields = ['ptlgas_f_mol_GK11', 'ptlgas_f_mol_GD14', 
				'ptlgas_f_mol_K13', 'ptlgas_f_mol_S14', 'ptlgas_f_neutral_H'])
			
	return

extractParticles()