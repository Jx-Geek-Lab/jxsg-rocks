import bpy

import math
import random
import string
from mathutils import Vector

class Utils:
    
    def translate(self, x, y, z):
        bpy.ops.transform.translate(value=(x, y, z), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    
    def rotate(self, axis, degree):
        bpy.ops.transform.rotate(value=math.radians(degree), orient_axis=axis.upper(), orient_type='VIEW')
    
    def scale(self, value):
        bpy.ops.transform.resize(value=(value, value, value), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True))
    
    def scale_by_x(self, value):
        bpy.ops.transform.resize(value=(value, 1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False))
    
    def scale_by_y(self, value):
        bpy.ops.transform.resize(value=(1, value, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False))
    
    def scale_by_z(self, value):
        bpy.ops.transform.resize(value=(1, 1, value), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))
    
    def scale_not_by_x(self, value):
        bpy.ops.transform.resize(value=(1, value, value), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, True))
    
    def scale_not_by_y(self, value):
        bpy.ops.transform.resize(value=(value, 1, value), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, True))
    
    def scale_not_by_z(self, value):
        bpy.ops.transform.resize(value=(value, value, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, False))
    
    def active(self, name):
        for object in bpy.context.view_layer.objects:
            if object and object.name:
                if name == object.name:
                    object.select_set(True)
                    bpy.context.view_layer.objects.active = object
    
    def random_rotation(self):
        self.rotate("x", random.randint(0, 720) - 360)
        self.rotate("y", random.randint(0, 720) - 360)
        self.rotate("z", random.randint(0, 720) - 360)
    
    def name(self, context, i):
        return context.scene.jxsg_main_settings.name_template.replace("*", "0" * (4 - len(str(i + context.scene.jxsg_main_settings.seek_index))) + str(i + context.scene.jxsg_main_settings.seek_index))
    
    def before_generation_starts(self, context):
        
        if context.scene.jxsg_main_settings.debug_mode:
            for object in bpy.data.objects:
                if object.name.startswith(context.scene.jxsg_main_settings.name_template.replace("*", "")):
                    bpy.data.objects.remove(object)
            for collection in context.scene.collection.children:
                context.scene.collection.children.unlink(collection)
        
        if context.scene.jxsg_rocks_generator_settings.use_rock_name_template:
            template = "O_Rock"
            if not "None" == context.scene.jxsg_rocks_generator_settings.deform_preset and not "Noise" == context.scene.jxsg_rocks_generator_settings.deform_preset:
                template = template + "_" + context.scene.jxsg_rocks_generator_settings.deform_preset
            template = template + ".*"
            context.scene.jxsg_main_settings.name_template = template
        
    def after_generation_ends(self, context):
        
        if not context.scene.jxsg_main_settings.debug_mode:
            context.scene.jxsg_main_settings.seek_index = context.scene.jxsg_main_settings.seek_index + context.scene.jxsg_main_settings.number_of_generations
            context.scene.jxsg_main_settings.starting_position_by_axis_y = context.scene.jxsg_main_settings.starting_position_by_axis_y + context.scene.jxsg_main_settings.offset_on_step_by_axis_x

class Executor(Utils):
    
    def rock(self, context, i):
        
        scene = context.scene
        
        task = scene.jxsg_rocks_generator_settings
        settings = scene.jxsg_main_settings
        
        previous = None
        
        random.seed(''.join(random.choice(string.ascii_letters) for i in range(16)), version=2)
        
        x = settings.starting_position_by_axis_x + (i * settings.offset_on_step_by_axis_x)
        y = settings.starting_position_by_axis_y + (i * settings.offset_on_step_by_axis_y)
        z = settings.starting_position_by_axis_z + (i * settings.offset_on_step_by_axis_z)
        
        for j in range(task.merge_count + 1):
            
            if previous is not None:
                previous.name = previous.name + ".Temp"
            
            if "Cube" == task.base_shape:
                bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            
            if "Sphere" == task.base_shape:
                bpy.ops.mesh.primitive_ico_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            
            if "Cylinder" == task.base_shape:
                bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            
            current = bpy.context.active_object
            current.name = self.name(context, i)
            
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            
            for j in range(task.bisect_count):
                bpy.ops.mesh.bisect(plane_co=(-14.7621, -2.03854, 2.01026), plane_no=(-9.81841e-17, 0.442182, 0.896926), use_fill=True, clear_outer=True, xstart=275, xend=632, ystart=391, yend=215, flip=False)
                bpy.ops.mesh.select_all(action='SELECT')
                self.random_rotation()
            
            if task.randomize_vertices:
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.transform.vertex_random(offset=random.randint(1,9) / 100, seed=random.randint(1,500))
            
            
            if "Plate" == context.scene.jxsg_rocks_generator_settings.deform_preset:
                bpy.ops.mesh.select_all(action='SELECT')
                self.scale_not_by_z(2)
                self.scale(0.5)
                if "2X" == context.scene.jxsg_rocks_generator_settings.plate_deform_preset:
                    self.scale_by_x(2)
                if "2Y" == context.scene.jxsg_rocks_generator_settings.plate_deform_preset:
                    self.scale_by_y(2)
                if "XY" == context.scene.jxsg_rocks_generator_settings.plate_deform_preset:
                    self.scale_not_by_z(2)
            
            if "Megalith" == context.scene.jxsg_rocks_generator_settings.deform_preset:
                bpy.ops.mesh.select_all(action='SELECT')
                if "None" == context.scene.jxsg_rocks_generator_settings.megalith_deform_preset:
                    self.scale_not_by_z(2)
                    self.scale(0.75)
                    self.scale_by_z(4)
                if "Beam" == context.scene.jxsg_rocks_generator_settings.megalith_deform_preset:
                    self.scale_not_by_z(0.5)
                    self.scale_by_z(4)
                if "Spear" == context.scene.jxsg_rocks_generator_settings.megalith_deform_preset:
                    self.scale_by_z(4)
                
            if "Monolith" == context.scene.jxsg_rocks_generator_settings.deform_preset:  
                bpy.ops.object.mode_set(mode="OBJECT")
                bpy.ops.object.add(type='LATTICE', enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                lattice = bpy.context.active_object
                lattice.name = current.name + ".Lattice"
                self.active(current.name)
                bpy.ops.object.modifier_add(type='LATTICE')
                bpy.context.object.modifiers["Lattice"].object = bpy.data.objects[lattice.name]
                self.active(lattice.name)
                for point in lattice.data.points:
                    x, y, z = point.co
                    if 0 > z:
                        point.co_deform = Vector((x, y, -0.5))
                    if 0 < z:
                        point.co_deform = Vector((x, y, 3 - z))
                bpy.ops.object.modifier_apply(modifier="Lattice")
                bpy.data.objects.remove(lattice)
                self.active(current.name)
                
            bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
            bpy.ops.object.mode_set(mode="OBJECT")
            
            if context.scene.jxsg_rocks_generator_settings.cut_from_the_bottom:
                bpy.ops.mesh.primitive_cube_add(size=8, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                object = bpy.context.active_object
                self.translate(0, 0, -4.25)
                self.active(current.name)
                bpy.ops.object.modifier_add(type='BOOLEAN')
                bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
                bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[object.name]
                bpy.ops.object.modifier_apply(modifier="Boolean")
                bpy.data.objects.remove(object)
                self.active(current.name)
            
            self.translate(x, y, z)
            
            if previous is not None:
                bpy.ops.object.modifier_add(type='BOOLEAN')
                bpy.context.object.modifiers["Boolean"].object = bpy.data.objects[previous.name]
                bpy.context.object.modifiers["Boolean"].operation = 'UNION'
                bpy.ops.object.modifier_apply(modifier="Boolean")
                bpy.data.objects.remove(previous)
            
            previous = current
    
    def generate(self, context):
        
        self.before_generation_starts(context)
        
        for i in range(context.scene.jxsg_main_settings.number_of_generations):
            self.rock(context, i)
        
        self.after_generation_ends(context)

default_debug_mode=True
default_name_template="O_Mesh.*"
default_number_of_generations=5
default_seek_index=0
default_starting_position_by_axis_x=0.0
default_starting_position_by_axis_y=0.0
default_starting_position_by_axis_z=0.0
default_offset_on_step_by_axis_x=5.0
default_offset_on_step_by_axis_y=0.0
default_offset_on_step_by_axis_z=0.0

class cls_jxsg_MainSettingsGroup(bpy.types.PropertyGroup):
    debug_mode: bpy.props.BoolProperty(default=default_debug_mode, name=" Debug mode")
    name_template: bpy.props.StringProperty(default=default_name_template, name="")
    number_of_generations: bpy.props.IntProperty(default=default_number_of_generations, min=1, max=100, name="")
    seek_index: bpy.props.IntProperty(default=default_seek_index, min=0, max=1000, name="")
    starting_position_by_axis_x: bpy.props.FloatProperty(default=default_starting_position_by_axis_x, min=-100.0, max=100.0, name="X")
    starting_position_by_axis_y: bpy.props.FloatProperty(default=default_starting_position_by_axis_y, min=-100.0, max=100.0, name="Y")
    starting_position_by_axis_z: bpy.props.FloatProperty(default=default_starting_position_by_axis_z, min=-100.0, max=100.0, name="Z")
    offset_on_step_by_axis_x: bpy.props.FloatProperty(default=default_offset_on_step_by_axis_x, min=-10.0, max=10.0, name="X")
    offset_on_step_by_axis_y: bpy.props.FloatProperty(default=default_offset_on_step_by_axis_y, min=-10.0, max=10.0, name="Y")
    offset_on_step_by_axis_z: bpy.props.FloatProperty(default=default_offset_on_step_by_axis_z, min=-10.0, max=10.0, name="Z")

class cls_jxsg_RocksGeneratorSettingsGroup(bpy.types.PropertyGroup):
    use_rock_name_template: bpy.props.BoolProperty(default=True, name=" Use rock name templace")
    merge_count: bpy.props.IntProperty(default=0, min=0, max=5, name="")
    bisect_count: bpy.props.IntProperty(default=5, min = 5, max=50, name="")
    base_shape: bpy.props.EnumProperty(
        default = "Cube",
        items = [
            ("Cube", "Cube", "Cube", "Cube", 1),
            ("Sphere", "Sphere", "Sphere", "Sphere", 2),
            ("Cylinder", "Cylinder", "Cylinder", "Cylinder", 3),
        ],
        name = ""
    )
    randomize_vertices: bpy.props.BoolProperty(default=False, name=" Randomize vertices")
    deform_preset: bpy.props.EnumProperty(
        default = "None",
        items = [
            ("None", "None", "None", "None", 1),
            # ("Noise", "Noise", "Noise", "Noise", 2),
            ("Plate", "Plate", "Plate", "Plate", 3),
            ("Megalith", "Megalith", "Megalith", "Megalith", 4),
            # ("Monolith", "Monolith", "Monolith", "Monolith", 5),
        ],
        name = ""
    )
    plate_deform_preset: bpy.props.EnumProperty(
        default = "None",
        items = [
            ("None", "None", "None", "None", 1),
            ("2X", "2X", "2X", "2X", 2),
            ("2Y", "2Y", "2Y", "2Y", 3),
            ("XY", "XY", "XY", "XY", 4),
        ],
        name = ""
    )
    megalith_deform_preset: bpy.props.EnumProperty(
        default = "None",
        items = [
            ("None", "None", "None", "None", 1),
            ("Beam", "Beam", "Beam", "Beam", 2),
            ("Spear", "Spear", "Spear", "Spear", 3),
        ],
        name = ""
    )
    cut_from_the_top: bpy.props.BoolProperty(default=False, name=" Cut from the top")
    cut_from_the_bottom: bpy.props.BoolProperty(default=True, name=" Cut from the bottom")

class cls_jxsg_MainSettingsOperator(bpy.types.Operator):
    
    bl_idname = "object.jxsg_main_settings_operator"
    bl_label = "Drop to default"

    def execute(self, context):
        
        scene = context.scene
        settings = scene.jxsg_main_settings
        
        settings.debug_mode=default_debug_mode
        settings.name_template=default_name_template
        settings.number_of_generations=default_number_of_generations
        settings.seek_index=default_seek_index
        settings.starting_position_by_axis_x=default_starting_position_by_axis_x
        settings.starting_position_by_axis_y=default_starting_position_by_axis_y
        settings.starting_position_by_axis_z=default_starting_position_by_axis_z
        settings.offset_on_step_by_axis_x=default_offset_on_step_by_axis_x
        settings.offset_on_step_by_axis_y=default_offset_on_step_by_axis_y
        settings.offset_on_step_by_axis_z=default_offset_on_step_by_axis_z
        
        return {'FINISHED'}

class cls_jxsg_RocksGeneratorOperator(bpy.types.Operator):
    
    bl_idname = "object.jxsg_rocks_generator_operator"
    bl_label = "Start"

    def execute(self, context):
        
        Executor().generate(context)
        
        return {'FINISHED'}

class cls_jxsg_AddonGeneralPanel(bpy.types.Panel):
    
    bl_idname = "OBJECT_PT_jxsg_addon_general_panel"
    bl_label = "JX Smart Generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JXSG"

    def draw(self, context):
        pass

class cls_jxsg_MainSettingsPanel(bpy.types.Panel):
    
    bl_idname = "OBJECT_PT_jxsg_main_settings_panel"
    bl_label = "Main settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "OBJECT_PT_jxsg_addon_general_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        settings = scene.jxsg_main_settings
        
        layout.row().prop(settings, "debug_mode")
        
        row = layout.row()
        row.column().label(text = "Name template")
        row.column().prop(settings, "name_template")
        
        row = layout.row()
        row.column().label(text = "Number of generations")
        row.column().prop(settings, "number_of_generations")
        
        row = layout.row()
        row.column().label(text = "Seek index")
        row.column().prop(settings, "seek_index")
        
        layout.row().label(text = "Starting position by axis")
        row = layout.row()
        row.column().prop(settings, "starting_position_by_axis_x")
        row.column().prop(settings, "starting_position_by_axis_y")
        row.column().prop(settings, "starting_position_by_axis_z")
        
        layout.row().label(text = "Offset on step by axis")
        row = layout.row()
        row.column().prop(settings, "offset_on_step_by_axis_x")
        row.column().prop(settings, "offset_on_step_by_axis_y")
        row.column().prop(settings, "offset_on_step_by_axis_z")
        
        row = layout.row()
        row.scale_y = 2
        row.operator("object.jxsg_main_settings_operator")

class cls_jxsg_RocksGeneratorPanel(bpy.types.Panel):
    
    bl_idname = "OBJECT_PT_jxsg_rocks_generator_panel"
    bl_label = "Rocks generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "OBJECT_PT_jxsg_addon_general_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        settings = scene.jxsg_rocks_generator_settings
        
        layout.row().prop(settings, "use_rock_name_template")
        
        row = layout.row()
        row.column().label(text = "Merge count")
        row.column().prop(settings, "merge_count")
        
        row = layout.row()
        row.column().label(text = "Bisect count")
        row.column().prop(settings, "bisect_count")
        
        row = layout.row()
        row.column().label(text = "Base shape")
        row.column().prop(settings, "base_shape")
        
        layout.row().prop(settings, "randomize_vertices")
        
        row = layout.row()
        row.column().label(text = "Deform preset")
        row.column().prop(settings, "deform_preset")
        
        if "Plate" == settings.deform_preset:
            row = layout.row()
            row.column().label(text = "Plate deform preset")
            row.column().prop(settings, "plate_deform_preset")
        
        if "Megalith" == settings.deform_preset:
            row = layout.row()
            row.column().label(text = "Megalith deform preset")
            row.column().prop(settings, "megalith_deform_preset")
        
        if "Monolith" == settings.deform_preset:
            layout.row().prop(settings, "cut_from_the_top")
        
        layout.row().prop(settings, "cut_from_the_bottom")
        
        row = layout.row()
        row.scale_y = 2
        row.operator("object.jxsg_rocks_generator_operator")

__classes = [

    cls_jxsg_MainSettingsGroup,
    cls_jxsg_RocksGeneratorSettingsGroup,

    cls_jxsg_MainSettingsOperator,
    cls_jxsg_RocksGeneratorOperator,

    cls_jxsg_AddonGeneralPanel,
    cls_jxsg_MainSettingsPanel,
    cls_jxsg_RocksGeneratorPanel,
]

def register():
    
    for cls in __classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.jxsg_main_settings = bpy.props.PointerProperty(type=cls_jxsg_MainSettingsGroup)

    bpy.types.Scene.jxsg_rocks_generator_settings = bpy.props.PointerProperty(type=cls_jxsg_RocksGeneratorSettingsGroup)

def unregister():
    
    for cls in __classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
