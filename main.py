import os
import vtk
from caja_vtk import Caja
from montacargas import Montacargas
import time
import math

class EscenaAlmacen:
    """
    Clase que representa una escena de almacén con varios montacargas y una rampa.
    """
    
    def __init__(self):
        """
        Inicializa la escena con tres montacargas y una rampa.
        """
        self._renderizador = vtk.vtkRenderer()
        self._renderizador.SetBackground(0.1, 0.15, 0.2)
        
        # Crear tres montacargas con diferentes tamaños de cajas
        self._montacargas = []
        self._montacargas_backup = []  # Backup para reiniciar
        self._crear_montacargas()
        
        # Crear la rampa
        self._dimensiones_rampa = (6.0, 3.0, 2.0)
        self._rampa_actor = self._crear_rampa(*self._dimensiones_rampa)
        self._renderizador.AddActor(self._rampa_actor)
        
        # Outline para la rampa
        self._outline_rampa = self._crear_outline_rampa()
        self._renderizador.AddActor(self._outline_rampa)
        
        # Configurar cámara
        self._configurar_camara()
        
        # Variables para control de animación
        self._ventana = None
        self._interactor = None
        self._cajas_en_rampa = []
        
    def _crear_montacargas(self):
        """
        Crea tres montacargas con diferentes dimensiones de cajas.
        """
        dimensiones = [
            (1.0, 1.0, 1.0),
            (2.0, 1.0, 1.0),
            (1.0, 2.0, 1.0),
        ]
        
        posiciones = [
            (-7.0, -5.0, 0.0),
            (0.0, -5.0, 0.0),
            (7.0, -5.0, 0.0),
        ]
        
        ruta_base = os.path.dirname(__file__)
        ruta_textura = os.path.join(ruta_base, "textura.jpg")
        tiene_textura = os.path.isfile(ruta_textura)
        
        for i in range(3):
            montacargas = Montacargas(10, espaciado=1.1, dimensiones_caja=dimensiones[i])
            
            if tiene_textura:
                for caja in montacargas._cajas:
                    caja.aplicar_textura(ruta_textura)
            else:
                color_base = [
                    (0.7, 0.3, 0.3),
                    (0.3, 0.7, 0.3),
                    (0.3, 0.3, 0.7),
                ]
                
                for j, caja in enumerate(montacargas._cajas):
                    r = color_base[i][0] - (j % 5) * 0.05
                    g = color_base[i][1] - (j % 5) * 0.05
                    b = color_base[i][2] - (j % 5) * 0.05
                    caja.actor.GetProperty().SetColor(r, g, b)
            
            self._mover_montacargas(montacargas, posiciones[i])
            montacargas.añadir_actores_a_renderizador(self._renderizador)
            self._montacargas.append(montacargas)
    
    def _mover_montacargas(self, montacargas, posicion):
        """Mueve todas las cajas de un montacargas a una posición específica."""
        montacargas._plano_actor.SetPosition(posicion)
        
        for caja in montacargas._cajas:
            pos_actual = caja.actor.GetPosition()
            caja.actor.SetPosition(
                pos_actual[0] + posicion[0],
                pos_actual[1] + posicion[1],
                pos_actual[2] + posicion[2]
            )
    
    def _crear_rampa(self, largo, ancho, alto):
        """Crea una rampa rectangular."""
        rampa = vtk.vtkCubeSource()
        rampa.SetXLength(largo)
        rampa.SetYLength(ancho)
        rampa.SetZLength(alto)
        rampa.Update()
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(rampa.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.6)
        actor.GetProperty().SetOpacity(0.3)
        actor.SetPosition(0.0, 6.0, alto/2)
        
        return actor
    
    def _crear_outline_rampa(self):
        """Crea un outline para visualizar mejor los límites de la rampa."""
        largo, ancho, alto = self._dimensiones_rampa
        
        cubo = vtk.vtkCubeSource()
        cubo.SetXLength(largo)
        cubo.SetYLength(ancho)
        cubo.SetZLength(alto)
        cubo.Update()
        
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(cubo.GetOutputPort())
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 1.0, 0.0)
        actor.GetProperty().SetLineWidth(3)
        actor.SetPosition(0.0, 6.0, alto/2)
        
        return actor
    
    def _configurar_camara(self):
        """Configura la cámara para visualizar toda la escena."""
        camara = self._renderizador.GetActiveCamera()
        camara.SetPosition(-25.0, 0.0, 15.0)
        camara.SetFocalPoint(0.9, 0.0, -0.9)
        camara.SetViewUp(1.0, 0.0, 0.0)
    
    def _mover_caja_animado(self, caja, pos_inicial, pos_final, pasos=50):
        """
        Mueve una caja de forma animada desde pos_inicial a pos_final.
        """
        for i in range(pasos + 1):
            t = i / pasos
            t_suave = t * t * (3 - 2 * t)
            
            altura_arco = 3.0 * math.sin(t * math.pi)
            
            pos_actual = (
                pos_inicial[0] + (pos_final[0] - pos_inicial[0]) * t_suave,
                pos_inicial[1] + (pos_final[1] - pos_inicial[1]) * t_suave,
                pos_inicial[2] + (pos_final[2] - pos_inicial[2]) * t_suave + altura_arco
            )
            
            caja.actor.SetPosition(pos_actual)
            
            if self._ventana:
                self._ventana.Render()
                time.sleep(0.02)
    
    def animacion_1_acomodo_inicial(self):
        """
        ANIMACIÓN 1: Tomar una caja de cada montacargas y colocarla en la rampa sin importar el acomodo.
        """
        print("\n" + "="*70)
        print("ANIMACIÓN 1: ACOMODO INICIAL")
        print("Tomando una caja de cada montacargas...")
        print("="*70 + "\n")
        
        largo, ancho, alto = self._dimensiones_rampa
        posicion_rampa = (0.0, 6.0, alto/2)
        
        # Posiciones simples para las 3 cajas iniciales
        posiciones = [
            (posicion_rampa[0] - 1.5, posicion_rampa[1], 1.0),
            (posicion_rampa[0], posicion_rampa[1], 1.0),
            (posicion_rampa[0] + 1.5, posicion_rampa[1], 1.0),
        ]
        
        for idx, montacargas in enumerate(self._montacargas):
            if montacargas._cajas:
                caja = montacargas._cajas[0]
                dim = montacargas._dimensiones_caja
                pos_inicial = caja.actor.GetPosition()
                pos_final = (posiciones[idx][0], posiciones[idx][1], dim[2]/2 + 0.0)
                
                print(f"  Montacargas {idx+1} (dim {dim}): Moviendo caja...")
                self._mover_caja_animado(caja, pos_inicial, pos_final, pasos=40)
                
                self._cajas_en_rampa.append(caja)
                montacargas._cajas.remove(caja)
        
        print("\n✓ Acomodo inicial completado!\n")
        time.sleep(1)
    
    def animacion_2_maximo_espacio(self):
        """
        ANIMACIÓN 2: MAXIMIZAR ESPACIO OCUPADO
        Estrategia: Usar cajas grandes primero, llenar compactamente.
        """
        print("\n" + "="*70)
        print("ANIMACIÓN 2: PLAN DE MÁXIMO ESPACIO OCUPADO (Requisito 9-11)")
        print("Estrategia: Cajas grandes primero, llenado compacto")
        print("="*70 + "\n")
        
        plan = self._calcular_plan_maximo_ocupado()
        self._ejecutar_plan(plan, "MÁXIMO ESPACIO")
    
    def animacion_3_minimo_vacio(self):
        """
        ANIMACIÓN 3: MINIMIZAR ESPACIO VACÍO
        Estrategia: Optimizar huecos, mezclar tamaños de cajas.
        """
        print("\n" + "="*70)
        print("ANIMACIÓN 3: PLAN DE MÍNIMO ESPACIO VACÍO (Requisito 12-13)")
        print("Estrategia: Rellenar huecos, optimizar cada posición")
        print("="*70 + "\n")
        
        plan = self._calcular_plan_minimo_vacio()
        self._ejecutar_plan(plan, "MÍNIMO VACÍO")
    
    def _calcular_plan_maximo_ocupado(self):
        """
        Plan que maximiza el espacio ocupado: usa cajas grandes primero.
        """
        largo, ancho, alto = self._dimensiones_rampa
        plan = []
        
        # Recolectar cajas
        cajas_disponibles = []
        for idx_mont, montacargas in enumerate(self._montacargas):
            for caja in montacargas._cajas:
                dim = montacargas._dimensiones_caja
                cajas_disponibles.append({
                    'caja': caja,
                    'montacargas_idx': idx_mont,
                    'dimensiones': dim,
                    'volumen': dim[0] * dim[1] * dim[2],
                })
        
        # MAXIMIZAR: Ordenar por volumen DESCENDENTE
        cajas_disponibles.sort(key=lambda x: x['volumen'], reverse=True)
        
        # Sistema de ocupación simplificado
        ocupado_nivel_0 = []
        ocupado_nivel_1 = []
        posicion_rampa = (0.0, 6.0, alto/2)
        
        def intersecta(rect1, rect2):
            """Verifica si dos rectángulos se intersectan."""
            x1_min, y1_min, x1_max, y1_max = rect1
            x2_min, y2_min, x2_max, y2_max = rect2
            return not (x1_max <= x2_min or x2_max <= x1_min or 
                       y1_max <= y2_min or y2_max <= y1_min)
        
        def puede_colocar_en_nivel(px, py, dim, nivel):
            """Verifica si se puede colocar una caja en una posición."""
            # Calcular bounds de la caja
            x_min = px - dim[0]/2
            x_max = px + dim[0]/2
            y_min = py - dim[1]/2
            y_max = py + dim[1]/2
            
            # Verificar límites de la rampa
            if (x_min < -largo/2 or x_max > largo/2 or
                y_min < -ancho/2 or y_max > ancho/2):
                return False
            
            rect_nueva = (x_min, y_min, x_max, y_max)
            lista_ocupado = ocupado_nivel_0 if nivel == 0 else ocupado_nivel_1
            
            # Verificar colisiones
            for rect_existente in lista_ocupado:
                if intersecta(rect_nueva, rect_existente):
                    return False
            
            # Nivel 1 requiere soporte
            if nivel == 1:
                tiene_soporte = False
                for rect_base in ocupado_nivel_0:
                    if intersecta(rect_nueva, rect_base):
                        tiene_soporte = True
                        break
                return tiene_soporte
            
            return True
        
        # Colocar cajas
        for info_caja in cajas_disponibles:
            dim = info_caja['dimensiones']
            colocada = False
            
            # Intentar nivel 0 primero, luego nivel 1
            for nivel in range(2):
                if colocada:
                    break
                
                # Búsqueda en grid
                paso = 0.3
                for py in [y * paso - ancho/2 + dim[1]/2 for y in range(int(ancho/paso))]:
                    if colocada:
                        break
                    for px in [x * paso - largo/2 + dim[0]/2 for x in range(int(largo/paso))]:
                        if puede_colocar_en_nivel(px, py, dim, nivel):
                            # Colocar
                            altura_z = 0.0 + dim[2]/2 if nivel == 0 else 0.0 + dim[2] + dim[2]/2
                            pos_final = (
                                posicion_rampa[0] + px,
                                posicion_rampa[1] + py,
                                altura_z
                            )
                            
                            plan.append({
                                'caja': info_caja['caja'],
                                'montacargas_idx': info_caja['montacargas_idx'],
                                'posicion_final': pos_final,
                                'dimensiones': dim,
                                'nivel': nivel
                            })
                            
                            # Marcar como ocupado
                            x_min = px - dim[0]/2
                            x_max = px + dim[0]/2
                            y_min = py - dim[1]/2
                            y_max = py + dim[1]/2
                            rect = (x_min, y_min, x_max, y_max)
                            
                            if nivel == 0:
                                ocupado_nivel_0.append(rect)
                            else:
                                ocupado_nivel_1.append(rect)
                            
                            colocada = True
                            break
        
        return plan
    
    def _calcular_plan_minimo_vacio(self):
        """
        Plan que minimiza el espacio vacío: mezcla tamaños para rellenar huecos.
        """
        largo, ancho, alto = self._dimensiones_rampa
        plan = []
        
        # Recolectar cajas
        cajas_disponibles = []
        for idx_mont, montacargas in enumerate(self._montacargas):
            for caja in montacargas._cajas:
                dim = montacargas._dimensiones_caja
                cajas_disponibles.append({
                    'caja': caja,
                    'montacargas_idx': idx_mont,
                    'dimensiones': dim,
                    'area': dim[0] * dim[1],
                })
        
        # MINIMIZAR VACÍO: Ordenar para mezclar tamaños (pequeñas primero en este caso)
        cajas_disponibles.sort(key=lambda x: x['area'])
        
        ocupado_nivel_0 = []
        ocupado_nivel_1 = []
        posicion_rampa = (0.0, 6.0, alto/2)
        
        def intersecta(rect1, rect2):
            x1_min, y1_min, x1_max, y1_max = rect1
            x2_min, y2_min, x2_max, y2_max = rect2
            return not (x1_max <= x2_min or x2_max <= x1_min or 
                       y1_max <= y2_min or y2_max <= y1_min)
        
        def puede_colocar_en_nivel(px, py, dim, nivel):
            x_min = px - dim[0]/2
            x_max = px + dim[0]/2
            y_min = py - dim[1]/2
            y_max = py + dim[1]/2
            
            if (x_min < -largo/2 or x_max > largo/2 or
                y_min < -ancho/2 or y_max > ancho/2):
                return False
            
            rect_nueva = (x_min, y_min, x_max, y_max)
            lista_ocupado = ocupado_nivel_0 if nivel == 0 else ocupado_nivel_1
            
            for rect_existente in lista_ocupado:
                if intersecta(rect_nueva, rect_existente):
                    return False
            
            if nivel == 1:
                tiene_soporte = False
                for rect_base in ocupado_nivel_0:
                    if intersecta(rect_nueva, rect_base):
                        tiene_soporte = True
                        break
                return tiene_soporte
            
            return True
        
        # Colocar cajas con paso más fino para mejor optimización
        for info_caja in cajas_disponibles:
            dim = info_caja['dimensiones']
            colocada = False
            
            for nivel in range(2):
                if colocada:
                    break
                
                paso = 0.2  # Paso más fino
                for px in [x * paso - largo/2 + dim[0]/2 for x in range(int(largo/paso))]:
                    if colocada:
                        break
                    for py in [y * paso - ancho/2 + dim[1]/2 for y in range(int(ancho/paso))]:
                        if puede_colocar_en_nivel(px, py, dim, nivel):
                            altura_z = 0.0 + dim[2]/2 if nivel == 0 else 0.0 + dim[2] + dim[2]/2
                            pos_final = (
                                posicion_rampa[0] + px,
                                posicion_rampa[1] + py,
                                altura_z
                            )
                            
                            plan.append({
                                'caja': info_caja['caja'],
                                'montacargas_idx': info_caja['montacargas_idx'],
                                'posicion_final': pos_final,
                                'dimensiones': dim,
                                'nivel': nivel
                            })
                            
                            x_min = px - dim[0]/2
                            x_max = px + dim[0]/2
                            y_min = py - dim[1]/2
                            y_max = py + dim[1]/2
                            rect = (x_min, y_min, x_max, y_max)
                            
                            if nivel == 0:
                                ocupado_nivel_0.append(rect)
                            else:
                                ocupado_nivel_1.append(rect)
                            
                            colocada = True
                            break
        
        return plan
    
    def _ejecutar_plan(self, plan, nombre_plan):
        """Ejecuta un plan de colocación."""
        if not plan:
            print("⚠ No se pudo generar el plan\n")
            return
        
        largo, ancho = self._dimensiones_rampa[0], self._dimensiones_rampa[1]
        volumen_rampa = largo * ancho * 2.0
        volumen_ocupado = sum(p['dimensiones'][0] * p['dimensiones'][1] * p['dimensiones'][2] 
                             for p in plan)
        volumen_vacio = volumen_rampa - volumen_ocupado
        
        nivel_0 = sum(1 for p in plan if p['nivel'] == 0)
        nivel_1 = sum(1 for p in plan if p['nivel'] == 1)
        
        print(f"📊 Estadísticas del Plan '{nombre_plan}':")
        print(f"  • Total de cajas: {len(plan)}")
        print(f"  • Volumen rampa: {volumen_rampa:.2f} m³")
        print(f"  • Volumen ocupado: {volumen_ocupado:.2f} m³ ({(volumen_ocupado/volumen_rampa)*100:.1f}%)")
        print(f"  • Volumen vacío: {volumen_vacio:.2f} m³ ({(volumen_vacio/volumen_rampa)*100:.1f}%)")
        print(f"  • Nivel base: {nivel_0} cajas")
        print(f"  • Nivel apilado: {nivel_1} cajas\n")
        
        print("🚀 Iniciando movimiento de cajas...\n")
        
        for idx, plan_item in enumerate(plan):
            caja = plan_item['caja']
            pos_inicial = caja.actor.GetPosition()
            pos_final = plan_item['posicion_final']
            nivel = plan_item['nivel']
            
            nivel_texto = "BASE" if nivel == 0 else "APILADA"
            print(f"  [{idx+1}/{len(plan)}] {nivel_texto} - Montacargas {plan_item['montacargas_idx']+1}")
            
            self._mover_caja_animado(caja, pos_inicial, pos_final, pasos=30)
            self._cajas_en_rampa.append(caja)
            
            mont = self._montacargas[plan_item['montacargas_idx']]
            if caja in mont._cajas:
                mont._cajas.remove(caja)
        
        print(f"\n✓ Plan '{nombre_plan}' completado!\n")
        time.sleep(1)
    
    def _limpiar_cajas_rampa(self):
        """Limpia las cajas de la rampa y las devuelve a los montacargas."""
        print("\n🔄 Limpiando cajas de la rampa...")
        
        # Remover cajas de la rampa (sin animación para no hacer muy lento)
        for caja in self._cajas_en_rampa:
            # Mover fuera de vista
            caja.actor.SetPosition(100, 100, 100)
        
        self._cajas_en_rampa.clear()
        
        if self._ventana:
            self._ventana.Render()
        
        print("✓ Rampa limpiada\n")
        time.sleep(0.5)
    
    def _reiniciar_escena(self):
        """Reinicia la escena a su estado inicial."""
        print("\n🔄 Reiniciando escena...")
        
        # Limpiar renderizador
        self._renderizador.RemoveAllViewProps()
        
        # Guardar referencias
        ventana_temp = self._ventana
        interactor_temp = self._interactor
        
        # Reinicializar
        self.__init__()
        
        # Restaurar ventana e interactor
        self._ventana = ventana_temp
        self._interactor = interactor_temp
        
        if self._ventana:
            self._ventana.AddRenderer(self._renderizador)
            self._ventana.Render()
        
        print("✓ Escena reiniciada!\n")
    
    def iniciar_visualizacion(self):
        """Inicia la visualización de la escena."""
        self._ventana = vtk.vtkRenderWindow()
        self._ventana.AddRenderer(self._renderizador)
        self._ventana.SetSize(1280, 720)
        self._ventana.SetWindowName("Sistema de Optimización de Almacén")
        
        self._interactor = vtk.vtkRenderWindowInteractor()
        self._interactor.SetRenderWindow(self._ventana)
        
        estilo = vtk.vtkInteractorStyleTrackballCamera()
        self._interactor.SetInteractorStyle(estilo)
        
        self._ventana.Render()
        
        # Callbacks para las animaciones
        def on_key_press(obj, event):
            key = obj.GetKeySym()
            if key == '1':
                print("\n>>> Presionaste '1': Animación 1 - Acomodo inicial...")
                self._limpiar_cajas_rampa()
                self.animacion_1_acomodo_inicial()
            elif key == '2':
                print("\n>>> Presionaste '2': Animación 2 - Máximo espacio ocupado...")
                self._limpiar_cajas_rampa()
                self.animacion_2_maximo_espacio()
            elif key == '3':
                print("\n>>> Presionaste '3': Animación 3 - Mínimo espacio vacío...")
                self._limpiar_cajas_rampa()
                self.animacion_3_minimo_vacio()
            elif key == 'r':
                print("\n>>> Presionaste 'r': Reiniciando escena...")
                self._reiniciar_escena()
            elif key == 'c':
                print("\n>>> Presionaste 'c': Limpiando rampa...")
                self._limpiar_cajas_rampa()
        
        self._interactor.AddObserver('KeyPressEvent', on_key_press)
        
        print("\n" + "="*70)
        print("SISTEMA DE OPTIMIZACIÓN DE ALMACÉN ".center(70, "="))
        print("="*70)
        print("\n CONTROLES:")
        print("  [1] - Animación 1: Acomodo inicial")
        print("  [2] - Animación 2: Máximo espacio ocupado")
        print("  [3] - Animación 3: Mínimo espacio vacío")
        print("  [C] - Limpiar rampa")
        print("  [R] - Reiniciar escena completa")
        print("  [Mouse] - Rotar/Zoom cámara")
        print("  [Q] - Salir")
        print("\n" + "="*70)
        print("="*70 + "\n")
        
        self._interactor.Initialize()
        self._interactor.Start()


# Punto de entrada principal
if __name__ == "__main__":
    escena = EscenaAlmacen()
    escena.iniciar_visualizacion()
