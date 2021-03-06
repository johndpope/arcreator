import rabbyt
import numpy
import pyglet

import welder_kernel as kernel


class TilemapEventStruct(object):

    '''
    A small data structure so that the Event Grid class can keep track
    of changes on specific events and draw them if they have changed
    '''

    def __init__(self, x, y, tile_id, name, hue, direction, pattern):
        self.x = x
        self.y = y
        self.tile_id = tile_id
        self.name = name
        self.hue = hue
        self.direction = direction
        self.pattern = pattern


class TilemapEventGrid(object):

    '''
    A organizer class, organizes and updates the sprites for events and
    their background when they are drawn in the editor
    '''

    def __init__(self, map, cache, tileset=""):
        # set properties
        self.map = map
        self.cache = cache
        self.tileset_name = tileset
        # setup the rendering batch and the oarding groups
        # set up data containers
        self.events = {}
        self.sprites = {}
        self.graphics = []
        self.backgrounds = []
        # setup the outline image used for background sprites
        self.setupOutline()
        # update the sprites
        self.update()

    def setupOutline(self):
        '''
        draws an outline for the event and stores it so that it can be uses in sprites later
        '''
        outlineEdgePattern = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255))
        eventOutline = outlineEdgePattern.create_image(24, 24).get_texture()
        outlineBackPattern = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 80))
        background = outlineBackPattern.create_image(22, 22)
        eventOutline.blit_into(background, 1, 1, 0)
        self.eventOutline = eventOutline.get_image_data()

    def setEventGraphic(self, key):
        '''
        takes an event id as a key and updates the sprite graphic
        '''
        # get event
        event = self.events[key]
        # if the graphic is a tile
        if event.tile_id >= 384:
            bitmap = self.cache.Tile(
                self.tileset_name, event.tile_id, event.hue)
            if not bitmap:
                bitmap = self.cache.Tile(
                    self.tileset_name, event.tile_id, event.hue)
            if bitmap:
                rect = (5, 5, 22, 22)
        # other wise the graphic is a sprite
        else:
            bitmap = self.cache.Character(event.name, event.hue)
            if not bitmap:
                bitmap = self.cache.Character(event.name, event.hue)
            if bitmap:
                cw = bitmap.width // 4
                ch = bitmap.height // 4
                sx = event.pattern * cw
                sy = (event.direction - 2) // 2 * ch
                rect = (
                    sx + (cw - 22) // 2, bitmap.height - sy - ch // 2 - 5, 22, 22)
        # draw a portion of the event graphic
        if bitmap:
            image = pyglet.image.create(32, 32).get_texture()
            region = bitmap.get_region(*rect)
            image.blit_into(region, 5, 5, 0)
        xpos = event.x * 32 + 16
        ypos = ((self.map.height - event.y) * 32) - 32 + 16
        if key not in self.sprites or self.sprites[key][0] is None:
            sprite = None
            if bitmap:
                sprite = rabbyt.Sprite(image, x=xpos, y=ypos)
                self.graphics.append(sprite)
            background = rabbyt.Sprite(
                self.eventOutline.get_texture(), x=xpos, y=ypos)
            self.backgrounds.append(background)
            self.sprites[key] = [sprite, background]
        else:
            if bitmap:
                self.sprites[key][0].texture = image
            else:
                self.graphics.remove(self.sprites[key][0])
                self.sprites[key][0] = None

    def updateEvent(self, key):
        '''
        compares graphically relevant data to stored versions of the data
        for each event and sets the graphic to be updated if the data has changed
        '''
        # get event
        flag = False
        mapEvent = self.map.events[key]
        graphic = self.map.events[key].pages[0].graphic
        if key not in self.events:
            event = TilemapEventStruct(mapEvent.x, mapEvent.y, graphic.tile_id, graphic.character_name,
                                       graphic.character_hue, graphic.direction, graphic.pattern)
            self.events[key] = event
            flag = True
        else:
            event = self.events[key]
            if event.x != mapEvent.x:
                event.x = mapEvent.x
            if event.y != mapEvent.x:
                event.y = mapEvent.y
            xpos = event.x * 32 + 16
            ypos = ((self.map.height - event.y) * 32) - 32 + 16
            if key in self.sprites:
                if self.sprites[key][0] is not None:
                    if self.sprites[key][0].x != xpos or self.sprites[key][0].y != ypos:
                        self.sprites[key][0].xy = xpos, ypos
                    if self.sprites[key][1].x != xpos or self.sprites[key][1].y != ypos:
                        self.sprites[key][1].xy = xpos, ypos
            if event.tile_id != graphic.tile_id:
                flag = True
                event.tile_id = graphic.tile_id
            if event.name != graphic.character_name:
                flag = True
                event.name = graphic.character_name
            if event.hue != graphic.character_hue:
                flag = True
                event.hue = graphic.character_hue
            if event.direction != graphic.direction:
                flag = True
                event.direction = graphic.direction
            if event.pattern != graphic.pattern:
                flag = True
                event.pattern = graphic.pattern
        if flag:
            self.setEventGraphic(key)
        # test values that are drawn to see if the graphic (or position) need
        # to be updated

    def update(self):
        '''
        loops through every event and removes sprites for events that have been deleted,
        then calls the updateEvent method for the rest of the events
        '''
        b = set(self.map.events.keys())
        a = list(self.events.keys())
        removed = [x for x in a if x not in b]
        for key in removed:
            self.graphics.remove(self.sprites[key][0])
            self.backgrounds.remove(self.sprites[key][1])
            del self.events[key]
            del self.sprites[key]
        for key in self.map.events.keys():
            self.updateEvent(key)

    def Draw(self):
        '''
        Draws the rendering batch and thus all the attached sprites
        '''
        rabbyt.render_unsorted(self.backgrounds)
        rabbyt.render_unsorted(self.graphics)


class TilemapTileGrid(object):

    '''
    A container and organizer class. maintains sprites that form a transparent
    grid over the tilemap when in the event mode
    '''

    def __init__(self, map):
        # store the map
        self.map = map
        # create an image for the sprites
        self.grid_image = pyglet.image.create(32, 32)
        # get a rendering batch to draw the grid quickly
        self.renderingBatch = pyglet.graphics.Batch()
        # setup the grid image
        self.setupGridImage()
        # create all the sprites in the grid and store them in a numpy array of
        # dtype object
        self.sprites = self.createGrid()

    def setupGridImage(self):
        '''
        draws the black outline around the edge of the tile
        '''
        self.black_pattern = pyglet.image.SolidColorImagePattern(
            (0, 0, 0, 255))
        self.grid_image = self.black_pattern.create_image(32, 32).get_texture()
        self.cut_pattern = pyglet.image.create(30, 30)
        self.grid_image.blit_into(self.cut_pattern, 1, 1, 0)

    def createGrid(self):
        '''
        loops through the maps x and y to create all the necessary sprites
        '''
        shape = (self.map.width, self.map.height)
        sprites = numpy.empty(shape, dtype=object)
        for x in range(shape[0]):
            for y in range(shape[1]):
                sprite = self.makeSprite(x, y)
                sprites[x, y] = sprite
        return sprites

    def makeSprite(self, x, y):
        xpos = x * 32 + 16
        ypos = ((self.map.height - y) * 32) - 32 + 16
        sprite = rabbyt.Sprite(self.grid_image.get_texture(), x=xpos, y=ypos)
        sprite.alpha = 0.3
        return sprite

    def update(self):
        '''
        updates the sprites in the grid so that if the map size changes the grid changes too
        '''
        # if it isn't the same size as the map
        shape = (self.map.width, self.map.height)
        if self.sprites.shape != shape:
            self.resize(*shape)

    def Draw(self, x, y, width, height):
        '''
        draws the rendering batch and thus all the attached sprites
        '''
        rabbyt.render_unsorted(
            self.sprites[x:x + width, y:y + height].flatten())

    def resize(self, xsize=1, ysize=1):
        '''
        '''
        newdata = numpy.empty((xsize, ysize), dtype=object)
        shape = self.sprites.shape
        mask = [0, 0, 0]
        if xsize >= shape[0]:
            mask[0] = shape[0]
        else:
            mask[0] = xsize
        if ysize >= shape[1]:
            mask[1] = shape[1]
        else:
            mask[1] = ysize
        newdata[:mask[0], :mask[1]] = self.sprites[:mask[0], :mask[1]]
        self.sprites = newdata
        shape = self.sprites.shape
        for x in range(shape[0]):
            for y in range(shape[1]):
                if self.sprites[x, y] is None:
                    self.sprites[x, y] = self.makeSprite(x, y)
                else:
                    xpos = x * 32 + 16
                    ypos = ((self.map.height - y) * 32) - 32 + 16
                    self.sprites[x, y].xy = xpos, ypos


class Tilemap(object):

    def __init__(self, cache, table, tileset="", autotiles=[]):
        # get the cache
        self.cache = cache

        self.table = table
        self.tile_ids = numpy.zeros(self.table.getShape(), order='F')
        self.blank_tile = pyglet.image.create(32, 32)

        # diming image
        self.dimmingImagePatteren = None
        self.dimmingImage = None

        # diming sprite
        self.dimmingSprite = None
        self.dimmingSpriteWidth = 0
        self.dimmingSpriteHeight = 0

        # active layer
        self.activeLayer = 0

        # bool for turning on layer diming on and off
        self.LayerDimming = True

        # autotile names
        self.autotile_names = autotiles
        # tileset name
        self.tileset_name = tileset

        self.tiles = self.createTilemap()

    def updateDimmingSprite(self, width, height, scale):
        '''
        updates the diming sprite
        '''
        if width != self.dimmingSpriteWidth or height != self.dimmingSpriteHeight or scale != self.dimmingSprite.scale:
            self.dimmingSpriteWidth = width
            self.dimmingSpriteHeight = height
            if self.dimmingImagePatteren is None:
                self.dimmingImagePatteren = pyglet.image.SolidColorImagePattern((0, 0, 0, 255))
            self.dimmingImage = self.dimmingImagePatteren.create_image(
                width, height).get_texture()
            self.dimmingSprite = rabbyt.Sprite(self.dimmingImage, x=0, y=0)
            self.dimmingSprite.alpha = 0.7
            self.dimmingSprite.scale = scale

    def setDimXY(self, x, y):
        '''
        set the xy of the diming sprite
        '''
        if self.dimmingSprite is not None:
            self.dimmingSprite.xy = x, y

    def createTilemap(self):
        '''
        create the tilemap
        '''
        shape = self.table.getShape()
        sprites = numpy.empty(shape, dtype=object, order='F')
        for x in range(shape[0]):
            for y in range(shape[1]):
                for z in range(shape[2]):
                    sprites[x, y, z] = self.makeSprite(x, y, z)
        return sprites

    def resizeTilemap(self, tiles, shape):
        newtiles = numpy.empty(shape, dtype=object, order='F')
        mask = [0, 0, 0]
        tileshape = tiles.shape
        if shape[0] >= tileshape[0]:
            mask[0] = tileshape[0]
        else:
            mask[0] = shape[0]
        if shape[1] >= tileshape[1]:
            mask[1] = tileshape[1]
        else:
            mask[1] = shape[1]
        if shape[2] >= tileshape[2]:
            mask[2] = tileshape[2]
        else:
            mask[2] = shape[2]
        newtiles[:mask[0], :mask[1], :mask[2]] = tiles[
            :mask[0], :mask[1], :mask[2]]
        indexes = numpy.argwhere(newtiles == numpy.array([None]))
        for x, y, z in indexes:
            newtiles[x, y, z] = self.makeSprite(x, y, z)
        return newtiles

    def resizeTileIDs(self, newshape):
        newids = numpy.zeros(newshape, dtype=numpy.int16, order='F')
        shape = self.tile_ids.shape
        mask = [0, 0, 0]
        if newshape[0] >= shape[0]:
            mask[0] = shape[0]
        else:
            mask[0] = newshape[0]
        if newshape[1] >= shape[1]:
            mask[1] = shape[1]
        else:
            mask[1] = newshape[1]
        if newshape[2] >= shape[2]:
            mask[2] = shape[2]
        else:
            mask[2] = newshape[2]
        newids[:mask[0], :mask[1], :mask[2]] = self.tile_ids[
            :mask[0], :mask[1], :mask[2]]
        self.tile_ids = newids

    def makeSprite(self, x, y, z, texture=None):
        xpos = x * 32 + 16
        ypos = ((self.table.getShape()[1] - y) * 32) - 32 + 16
        if texture is None:
            texture = self.blank_tile.get_texture()
        sprite = rabbyt.Sprite(texture, x=xpos, y=ypos)
        return sprite

    def update(self):
        '''
        checks for change in tile ids and updates the tilemap
        '''
        # if the arn't the same size
        if self.tile_ids.shape != self.table.getShape():
            self.resize(*self.table.getShape())
        # find the tiles who's ids have changed
        indexes = numpy.argwhere(self.table._data != self.tile_ids)
        # we have the idexes of the tiles we need to update so copy
        # the changed data over so we don;t have to update again
        self.tile_ids[:] = self.table._data[:]
        for index in indexes:
            self.set_image(tuple(index), self.tile_ids[tuple(index)])

    def set_image(self, index, tid):
        '''
        change the bitmap of a tile (by making a new sprite)
        '''
        # if for some reason the sprite does not exist (ie. the map was
        # resized) make it
        x, y, z = index
        if self.tiles[index] is None:
            self.tiles[index] = self.makeSprite(x, y, z)

        # get the tile bitmap
        if tid < 384:
            if tid <= 47:
                bitmap = self.blank_tile
            else:
                # get the filename
                autotile = self.autotile_names[int(tid) // 48 - 1]
                # get the right pattern
                pattern = tid % 48
                # collect the tile form the cache checking the local project folder
                # and the system RTP folder
                bitmap = self.cache.AutotilePattern(autotile, pattern)
                if not bitmap:
                    bitmap = self.cache.AutotilePattern(autotile, pattern)
                if not bitmap:
                    bitmap = self.blank_tile
        # normal tile
        else:
            # get the tile bitmap
            bitmap = self.cache.Tile(self.tileset_name, tid, 0)
            if not bitmap:
                bitmap = self.cache.Tile(self.tileset_name, tid, 0)
            if not bitmap:
                bitmap = self.blank_tile
        # draw the tile to the surface
        self.tiles[index].texture = bitmap.get_texture()

    def SetLayerOpacity(self, layer, opacity):
        '''
        sets the alpha of all the sprite in a layer
        '''
        layer = self.tiles[:, :, layer]
        for sprite in layer.flatten():
            sprite.alpha = opacity

    def SetActiveLayer(self, layer):
        '''
        sets the active layer, diming or changing alpha as needed
        '''
        self.activeLayer = layer
        if layer == (self.table.getShape()[2] + 1):
            for z in range(self.table.getShape()[2]):
                self.SetLayerOpacity(z, 1.0)
        else:
            if self.LayerDimming:
                for z in range(self.table.getShape()[2]):
                    if z <= self.activeLayer:
                        self.SetLayerOpacity(z, 1.0)
                    else:
                        self.SetLayerOpacity(z, 0.3)

    def SetLayerDimming(self, bool):
        '''
        turns layer diming on and off, setting the alpha of the layers as needed
        '''
        self.LayerDimming = bool
        if self.LayerDimming:
            for z in range(self.table.getShape()[2]):
                if z <= self.activeLayer:
                    self.SetLayerOpacity(z, 1.0)
                else:
                    self.SetLayerOpacity(z, 0.3)
        else:
            for z in range(self.table.getShape()[2]):
                self.SetLayerOpacity(z, 1.0)

    def Draw(self, x, y, width, height):
        '''
        draw the layers of the map
        '''
        on_screen = self.tiles[x:x + width, y:y + height]
        if not self.LayerDimming or self.activeLayer > on_screen.shape[2]:
            # draw the dimlayer first
            self.dimmingSprite.render()
        for z in range(on_screen.shape[2]):
            if z == self.activeLayer and self.LayerDimming:
                if self.dimmingSprite is not None:
                    self.dimmingSprite.render()
            rabbyt.render_unsorted(on_screen[:, :, z].flatten())


class TilemapMouseSprite(object):

    def __init__(self, map):
        # setup data
        self.map = map
        self.cornerSprites = []
        self.topRowSprites = []
        self.bottomRowSprites = []
        self.horizontalSprites = []
        self.leftRowSprites = []
        self.rightRowSprites = []
        self.verticalsprites = []
        self.TBCorners = []
        self.LRCorners = []
        self.sprites = []
        self.singleMode = False
        self.topLeftPos = [-1, -1]
        self.bottomRightPos = [-1, -1]
        # create images to use
        self.setupImages()
        # create the sprites
        self.setupSprites()

    def setupImages(self):
        # get out solid color patterns
        blackPattern = pyglet.image.SolidColorImagePattern((0, 0, 0, 255))
        whitePattern = pyglet.image.SolidColorImagePattern(
            (255, 255, 255, 255))
        # create the single image
        self.singleImage = blackPattern.create_image(32, 32).get_texture()
        whiteInner = whitePattern.create_image(30, 30)
        self.singleImage.blit_into(whiteInner, 1, 1, 0)
        blackInner = blackPattern.create_image(26, 26)
        self.singleImage.blit_into(blackInner, 3, 3, 0)
        clearInner = pyglet.image.create(24, 24)
        self.singleImage.blit_into(clearInner, 4, 4, 0)
        # get the pieces to construct the other sprites from the single sprite
        TLCorner = self.singleImage.get_region(0, 16, 16, 16).get_image_data()
        BLCorner = self.singleImage.get_region(0, 0, 16, 16).get_image_data()
        TRCorner = self.singleImage.get_region(16, 16, 16, 16).get_image_data()
        BRCorner = self.singleImage.get_region(16, 0, 16, 16).get_image_data()
        striateBH = self.singleImage.get_region(8, 0, 16, 16).get_image_data()
        striateLV = self.singleImage.get_region(0, 8, 16, 16).get_image_data()
        striateTH = self.singleImage.get_region(8, 16, 16, 16).get_image_data()
        striateRV = self.singleImage.get_region(16, 8, 16, 16).get_image_data()
        # Top Left corner
        self.TLCorner = pyglet.image.create(32, 32).get_texture()
        self.TLCorner.blit_into(TLCorner, 0, 16, 0)
        self.TLCorner.blit_into(striateLV, 0, 0, 0)
        self.TLCorner.blit_into(striateTH, 16, 16, 0)
        # Bottom Left corner
        self.BLCorner = pyglet.image.create(32, 32).get_texture()
        self.BLCorner.blit_into(BLCorner, 0, 0, 0)
        self.BLCorner.blit_into(striateLV, 0, 16, 0)
        self.BLCorner.blit_into(striateBH, 16, 0, 0)
        # Top Right corner
        self.TRCorner = pyglet.image.create(32, 32).get_texture()
        self.TRCorner.blit_into(TRCorner, 16, 16, 0)
        self.TRCorner.blit_into(striateRV, 16, 0, 0)
        self.TRCorner.blit_into(striateTH, 0, 16, 0)
        # Bottom Right corner
        self.BRCorner = pyglet.image.create(32, 32).get_texture()
        self.BRCorner.blit_into(BRCorner, 16, 0, 0)
        self.BRCorner.blit_into(striateRV, 16, 16, 0)
        self.BRCorner.blit_into(striateBH, 0, 0, 0)
        # Left Vertical
        self.LeftV = pyglet.image.create(32, 32).get_texture()
        self.LeftV.blit_into(striateLV, 0, 0, 0)
        self.LeftV.blit_into(striateLV, 0, 16, 0)
        # Right Vertical
        self.RightV = pyglet.image.create(32, 32).get_texture()
        self.RightV.blit_into(striateRV, 16, 0, 0)
        self.RightV.blit_into(striateRV, 16, 16, 0)
        # Left Corners
        self.LeftC = pyglet.image.create(32, 32).get_texture()
        self.LeftC.blit_into(BLCorner, 0, 0, 0)
        self.LeftC.blit_into(TLCorner, 0, 16, 0)
        self.LeftC.blit_into(striateTH, 16, 16, 0)
        self.LeftC.blit_into(striateBH, 16, 0, 0)
        # Right Corners
        self.RightC = pyglet.image.create(32, 32).get_texture()
        self.RightC.blit_into(TRCorner, 16, 16, 0)
        self.RightC.blit_into(BRCorner, 16, 0, 0)
        self.RightC.blit_into(striateTH, 0, 16, 0)
        self.RightC.blit_into(striateBH, 0, 0, 0)
        # Top Corners
        self.TopC = pyglet.image.create(32, 32).get_texture()
        self.TopC.blit_into(TRCorner, 16, 16, 0)
        self.TopC.blit_into(TLCorner, 0, 16, 0)
        self.TopC.blit_into(striateLV, 0, 0, 0)
        self.TopC.blit_into(striateRV, 16, 0, 0)
        # Bottom Corners
        self.BottomC = pyglet.image.create(32, 32).get_texture()
        self.BottomC.blit_into(BLCorner, 0, 0, 0)
        self.BottomC.blit_into(BRCorner, 16, 0, 0)
        self.BottomC.blit_into(striateLV, 0, 16, 0)
        self.BottomC.blit_into(striateRV, 16, 16, 0)
        # Top Horizontal
        self.TopH = pyglet.image.create(32, 32).get_texture()
        self.TopH.blit_into(striateTH, 0, 16, 0)
        self.TopH.blit_into(striateTH, 16, 16, 0)
        # Bottom Horizontal
        self.BottomH = pyglet.image.create(32, 32).get_texture()
        self.BottomH.blit_into(striateBH, 0, 0, 0)
        self.BottomH.blit_into(striateBH, 16, 0, 0)

    def makeSprite(self, type, x=-1, y=-1):
        # correct range
        if type < 0:
            type = 0
        if type > 11:
            type = 11
        # create the right sprite
        if type == 0:  # TLC
            sprite = rabbyt.Sprite(self.TLCorner.get_texture(), x=x * 32, y=y * 32)
        elif type == 1:  # TRC
            sprite = rabbyt.Sprite(self.TRCorner.get_texture(), x=x * 32, y=y * 32)
        elif type == 2:  # BLC
            sprite = rabbyt.Sprite(self.BLCorner.get_texture(), x=x * 32, y=y * 32)
        elif type == 3:  # BRC
            sprite = rabbyt.Sprite(self.BRCorner.get_texture(), x=x * 32, y=y * 32)
        elif type == 4:  # TH
            sprite = rabbyt.Sprite(self.TopH.get_texture(), x=x * 32, y=y * 32)
        elif type == 5:  # BH
            sprite = rabbyt.Sprite(self.BottomH.get_texture(), x=x * 32, y=y * 32)
        elif type == 6:  # LV
            sprite = rabbyt.Sprite(self.LeftV.get_texture(), x=x * 32, y=y * 32)
        elif type == 7:  # RV
            sprite = rabbyt.Sprite(self.RightV.get_texture(), x=x * 32, y=y * 32)
        elif type == 8:  # LC
            sprite = rabbyt.Sprite(self.LeftC.get_texture(), x=x * 32, y=y * 32)
        elif type == 9:  # RC
            sprite = rabbyt.Sprite(self.RightC.get_texture(), x=x * 32, y=y * 32)
        elif type == 10:  # TC
            sprite = rabbyt.Sprite(self.TopC.get_texture(), x=x * 32, y=y * 32)
        elif type == 11:  # BC
            sprite = rabbyt.Sprite(self.BottomC.get_texture(), x=x * 32, y=y * 32)
        # add the sprite to the sprites array so we can keep track of it
        self.sprites.append(sprite)
        # return the sprite
        return sprite

    def setupSprites(self):
        self.singleTileSprite = rabbyt.Sprite(
            self.singleImage.get_texture(), x=-1, y=-1)
        self.sprites.append(self.singleTileSprite)
        # make corner sprites
        for type in range(4):
            self.cornerSprites.append(self.makeSprite(type))
        # add the left right corners
        self.LRCorners.append(self.makeSprite(8))
        self.LRCorners.append(self.makeSprite(9))
        # add the top bottom corners
        self.TBCorners.append(self.makeSprite(10))
        self.TBCorners.append(self.makeSprite(11))

    def setTopLeft(self, x, y):
        self.topLeftPos[0] = x
        self.topLeftPos[1] = y

    def setBottomRight(self, x, y):
        self.bottomRightPos[0] = x
        self.bottomRightPos[1] = y

    def update(self):
        '''
        updates the positions of the sprite used to represent the mouse cursor
        '''
        fourCornersFlag = False
        verticalFlag = False
        horizontalFlag = False
        LRFlag = False
        TBFlag = False
        width = self.bottomRightPos[0] - self.topLeftPos[0]
        height = self.bottomRightPos[1] - self.topLeftPos[1]
        if self.singleMode or (width == 0 and height == 0):
            # update the positions of the single tile sprite
            self.singleTileSprite.xy = self.topLeftPos[
                0] * 32 + 16, ((self.map.height - self.topLeftPos[1]) * 32) - 32 + 16
        elif width != 0:
            if abs(width) > 1:
                horizontalFlag = True
            if height == 0:
                LRFlag = True
            else:
                fourCornersFlag = True
                if abs(height) > 1:
                    verticalFlag = True
        elif height != 0:
            if abs(height) > 1:
                verticalFlag = True
            if width == 0:
                TBFlag = True
            else:
                fourCornersFlag = True
                if abs(width) > 1:
                    horizontalFlag = True

        if width >= 0:
            TLx = self.topLeftPos[0]
            BRx = self.bottomRightPos[0]
        elif width < 0:
            TLx = self.bottomRightPos[0]
            BRx = self.topLeftPos[0]
        if height >= 0:
            TLy = self.map.height - self.topLeftPos[1]
            BRy = self.map.height - self.bottomRightPos[1]
        elif height < 0:
            TLy = self.map.height - self.bottomRightPos[1]
            BRy = self.map.height - self.topLeftPos[1]

        if horizontalFlag:
            # make sure that there is the right number of top row sprites
            if len(self.topRowSprites) < abs(width) - 1:
                for i in range(abs(width) - 1 - len(self.topRowSprites)):
                    self.topRowSprites.append(self.makeSprite(4))
            else:
                sprites = self.topRowSprites
                self.topRowSprites = sprites[:abs(width) - 1]
                for sprite in sprites[abs(width) - 1:]:
                    self.sprites.remove(sprite)
            # make sure that there is the right number of bottom row sprites
            if len(self.bottomRowSprites) < abs(width) - 1:
                for i in range(abs(width) - 1 - len(self.bottomRowSprites)):
                    self.bottomRowSprites.append(self.makeSprite(5))
            else:
                sprites = self.bottomRowSprites
                self.bottomRowSprites = sprites[:abs(width) - 1]
                for sprite in sprites[abs(width) - 1:]:
                    self.sprites.remove(sprite)
            # update the positions of the horizontal sprites
            for x in range(len(self.topRowSprites)):
                self.topRowSprites[x].xy = (
                    TLx + x + 1) * 32 + 16, (TLy * 32) - 32 + 16
                self.bottomRowSprites[x].xy = (
                    TLx + x + 1) * 32 + 16, (BRy * 32) - 32 + 16
        if verticalFlag:
            sprites = self.leftRowSprites
            # make sure that there is the right number of left row sprites
            if len(self.leftRowSprites) < abs(height) - 1:
                for i in range(abs(height) - 1 - len(self.leftRowSprites)):
                    self.leftRowSprites.append(self.makeSprite(6))
            else:
                sprites = self.leftRowSprites
                self.leftRowSprites = sprites[:abs(height) - 1]
                for sprite in sprites[abs(height) - 1:]:
                    self.sprites.remove(sprite)
            # make sure that there is the right number of right row sprites
            if len(self.rightRowSprites) < abs(height) - 1:
                for i in range(abs(height) - 1 - len(self.rightRowSprites)):
                    self.rightRowSprites.append(self.makeSprite(7))
            else:
                sprites = self.rightRowSprites
                self.rightRowSprites = sprites[:abs(height) - 1]
                for sprite in sprites[abs(height) - 1:]:
                    self.sprites.remove(sprite)
            # update the positions vertical sprites
            for y in range(len(self.leftRowSprites)):
                self.leftRowSprites[y].xy = TLx * 32 + \
                    16, ((TLy - y - 1) * 32) - 32 + 16
                self.rightRowSprites[y].xy = BRx * 32 + \
                    16, ((TLy - y - 1) * 32) - 32 + 16
        if TBFlag:
            # update the position of the top Bottom corners
            self.TBCorners[0].xy = TLx * 32 + 16, (TLy * 32) - 32 + 16
            self.TBCorners[1].xy = TLx * 32 + 16, (BRy * 32) - 32 + 16
        if LRFlag:
            # update positions of left right corners
            self.LRCorners[0].xy = TLx * 32 + 16, (TLy * 32) - 32 + 16
            self.LRCorners[1].xy = BRx * 32 + 16, (TLy * 32) - 32 + 16
        if fourCornersFlag:
            # update the positions of the corners sprites
            # TL
            self.cornerSprites[0].xy = TLx * 32 + 16, TLy * 32 - 32 + 16
            # TR
            self.cornerSprites[1].xy = BRx * 32 + 16, TLy * 32 - 32 + 16
            # BL
            self.cornerSprites[2].xy = TLx * 32 + 16, BRy * 32 - 32 + 16
            # BR
            self.cornerSprites[3].xy = BRx * 32 + 16, BRy * 32 - 32 + 16
        self.horizontalSprites = []
        self.horizontalSprites.extend(self.topRowSprites)
        self.horizontalSprites.extend(self.bottomRowSprites)
        self.verticalsprites = []
        self.verticalsprites.extend(self.leftRowSprites)
        self.verticalsprites.extend(self.rightRowSprites)

    def Draw(self):
        '''
        draws the rendering batchs to render the mouse sprites to the screen
        '''
        fourCornersFlag = False
        verticalFlag = False
        horizontalFlag = False
        LRFlag = False
        TBFlag = False
        width = self.bottomRightPos[0] - self.topLeftPos[0]
        height = self.bottomRightPos[1] - self.topLeftPos[1]
        if self.singleMode or (width == 0 and height == 0):
            # draw the single tile sprite
            self.singleTileSprite.render()
        elif width != 0:
            if abs(width) > 1:
                horizontalFlag = True
            if height == 0:
                LRFlag = True
            else:
                fourCornersFlag = True
                if abs(height) > 1:
                    verticalFlag = True
        elif height != 0:
            if abs(height) > 1:
                verticalFlag = True
            if width == 0:
                TBFlag = True
            else:
                fourCornersFlag = True
                if abs(width) > 1:
                    horizontalFlag = True

        if horizontalFlag:
            # draw the horizontal sprites
            rabbyt.render_unsorted(self.horizontalSprites)
        if verticalFlag:
            # draw the vertical sprites
            rabbyt.render_unsorted(self.verticalsprites)
            # draw the top and Bottom corners in two tiles
        if TBFlag:
            rabbyt.render_unsorted(self.TBCorners)
        if LRFlag:
            # draw the left and right corners in two tiles
            rabbyt.render_unsorted(self.LRCorners)
        if fourCornersFlag:
            # draw the four corner sprites
            rabbyt.render_unsorted(self.cornerSprites)


class TilemapMouseManager(object):

    def __init__(self, mapPanel, map, toolbar):
        self.map = map
        self.toolbar = toolbar
        self.mapPanel = mapPanel
        self.sprite = None
        self.topLeft = [-1, -1]
        self.bottomRight = [-1, -1]

    def setSprite(self, sprite):
        self.sprite = sprite

    def setTopLeft(self, x, y):
        if x != self.topLeft[0] or y != self.topLeft[1]:
            if x < 0:
                x = 0
            elif x > self.map.width - 1:
                x = self.map.width - 1
            if y < 0:
                y = 0
            elif y > self.map.height - 1:
                y = self.map.height - 1
            self.topLeft[0] = x
            self.topLeft[1] = y
            self.mapPanel.NeedRedraw = True
            if self.sprite is not None:
                self.sprite.setTopLeft(x, y)

    def setBottomRight(self, x, y):
        if x != self.bottomRight[0] or y != self.bottomRight[1]:
            if x < 0:
                x = 0
            elif x > self.map.width - 1:
                x = self.map.width - 1
            if y < 0:
                y = 0
            elif y > self.map.height - 1:
                y = self.map.height - 1
            self.bottomRight[0] = x
            self.bottomRight[1] = y
            self.mapPanel.NeedRedraw = True
            if self.sprite is not None:
                self.sprite.setBottomRight(x, y)

    def setSingleMode(self, value):
        if self.sprite is not None:
            self.sprite.singleMode = value
