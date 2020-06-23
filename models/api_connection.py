@api.multi
	def prueba(self):
		# Parametros de conexion:
		db = "copiaevolutionmedicalcenter"
		username ="api@test.com"
		password = "api.test"
		url = 'http://copiaevolutionmedicalcenter.clinicadigital.net'

		# Apuntando al EndPoint de Odoo
		common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
		uid = common.authenticate(db, username, password, {})
		models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

		# Se accede al objeto res.partner y se ejecuta el metodo check_access_rights
		read = models.execute_kw(db, uid, password,
		    'res.partner', 'check_access_rights',
		    ['read'], {'raise_exception': False})

		# Se listan registros de res.partner cuando el campo is_company es = True
		listar = models.execute_kw(db, uid, password,
			'res.partner', 'search',
			[[['is_company', '=', True]]])

		# Consultar el ultimo Id en res.partner
		ids = models.execute_kw(db, uid, password,
			'res.partner', 'search',
			[[['is_company', '=', True]]],
			{'limit': 1})

		# Consultar solo algunos campos en especifico.
		multi_consulta = models.execute_kw(db, uid, password,
			'res.partner', 'read',
			[ids], {'fields': ['name', 'country_id', 'comment']})

		# search_read() method
		consulta = models.execute_kw(db, uid, password,
			'res.partner', 'search_read',
			[[['is_company', '=', True]]],
			{'fields': ['name', 'country_id', 'comment'], 'limit': 5})

		# Create()
		partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
			'name': "New Partner",
			'email': "partner@new.com",
			}])
		print(partner_id)

		# Write()
		partner_id = models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], {
			'name': "New Partner",
			'email': "partner@new.com",
			}])
		print(partner_id)