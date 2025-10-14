import os
import vtk


class Caja:
	"""Representa una caja parametrizable con soporte opcional para textura."""

	_EXTENSIONES_TEX = {
		".jpg": vtk.vtkJPEGReader,
		".jpeg": vtk.vtkJPEGReader,
		".png": vtk.vtkPNGReader,
		".bmp": vtk.vtkBMPReader,
		".tiff": vtk.vtkTIFFReader,
		".tif": vtk.vtkTIFFReader,
	}

	def __init__(self, x, y, z, repeticiones):
		self._source = vtk.vtkCubeSource()
		self._source.SetXLength(x)
		self._source.SetYLength(y)
		self._source.SetZLength(z)
		self._repeticiones = repeticiones  # Número de repeticiones de textura por cara

		# Crear el cubo y generar las coordenadas de textura manualmente
		self._source.Update()
		self._apply_texture_coordinates()

		# Configuramos el mapper para renderizar
		self._mapper = vtk.vtkPolyDataMapper()
		self._mapper.SetInputConnection(self._source.GetOutputPort())

		self._actor = vtk.vtkActor()
		self._actor.SetMapper(self._mapper)
		self._texture = None

	@property
	def actor(self):
		return self._actor

	def _apply_texture_coordinates(self):
		"""Aplica coordenadas de textura personalizadas para permitir repetición."""
		poly_data = self._source.GetOutput()
		
		# Crear nuevas coordenadas de textura
		tcoords = vtk.vtkFloatArray()
		tcoords.SetNumberOfComponents(2)
		tcoords.SetName("TCoords")
		
		# Obtenemos los puntos del cubo para asignar textura
		n_points = poly_data.GetNumberOfPoints()
		
		# Para cada punto del cubo, establecemos coordenadas de textura repetidas
		# según el factor de repetición especificado
		rep = self._repeticiones  # Valor para repetir la textura
		
		# Las coordenadas de textura por defecto van de 0 a 1
		# Modificarlas para ir de 0 a 'rep' permitirá repetir la textura
		for i in range(n_points):
			# Obtenemos las coordenadas de textura existentes
			existing_tcoords = poly_data.GetPointData().GetTCoords()
			
			if existing_tcoords:
				s, t = existing_tcoords.GetTuple2(i)
				# Multiplicamos por el factor de repetición
				tcoords.InsertNextTuple2(s * rep, t * rep)
			else:
				# Si no hay coordenadas de textura, creamos unas por defecto
				tcoords.InsertNextTuple2(0, 0)
		
		# Asignamos las nuevas coordenadas de textura al polydata
		poly_data.GetPointData().SetTCoords(tcoords)
		poly_data.Modified()

	def actualizar_dimensiones(self, x=None, y=None, z=None, repeticiones=None):
		if x is not None:
			self._source.SetXLength(x)
		if y is not None:
			self._source.SetYLength(y)
		if z is not None:
			self._source.SetZLength(z)
		if repeticiones is not None:
			self._repeticiones = repeticiones
		
		self._source.Update()
		self._apply_texture_coordinates()

	def aplicar_textura(self, ruta, repeticiones=None):
		"""
		Aplica una textura al cubo con capacidad de repetición.
		
		:param ruta: Ruta al archivo de textura
		:param repeticiones: Opcional. Número de repeticiones de textura por cara
		"""
		if not os.path.isfile(ruta):
			raise FileNotFoundError(f"No se encontró la textura en '{ruta}'")

		extension = os.path.splitext(ruta)[1].lower()
		lector_cls = self._EXTENSIONES_TEX.get(extension)
		if lector_cls is None:
			raise ValueError(f"Extensión de textura no soportada: {extension}")

		lector = lector_cls()
		lector.SetFileName(ruta)
		lector.Update()

		textura = vtk.vtkTexture()
		textura.SetInputConnection(lector.GetOutputPort())
		textura.InterpolateOn()
		textura.RepeatOn()  # Activar repetición de textura
		textura.SetBlendingMode(vtk.vtkTexture.VTK_TEXTURE_BLENDING_MODE_REPLACE)

		self._texture = textura
		self._actor.SetTexture(textura)
		
		# Actualizar repeticiones si se proporcionaron
		if repeticiones is not None:
			self._repeticiones = repeticiones
			self._apply_texture_coordinates()

#Ejemplo de uso(Solo de prueba y se puede quitar)
if __name__ == "__main__":
	# Crear caja con repeticiones de textura
	caja = Caja(1.0, 1.0, 1.0, repeticiones=1)

	ruta_textura = os.path.join(os.path.dirname(__file__), "textura.jpg")
	caja.aplicar_textura(ruta_textura)

	renderizador = vtk.vtkRenderer()
	renderizador.AddActor(caja.actor)
	renderizador.SetBackground(0.1, 0.1, 0.1)

	ventana = vtk.vtkRenderWindow()
	ventana.AddRenderer(renderizador)
	ventana.SetSize(800, 600)

	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(ventana)

	ventana.Render()
	interactor.Initialize()
	interactor.Start()
