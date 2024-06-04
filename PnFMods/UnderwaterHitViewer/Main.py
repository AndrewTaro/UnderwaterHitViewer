API_VERSION = 'API_v1.0'
MOD_NAME = 'UnderwaterHitViewer'

try:
    import events, battle, ui, callbacks, utils
except:
    pass

COMPONENT_KEY = 'modUnderwaterHitViewer'
DISPLAY_TIME = 5.0

class UnderwaterHitViewer(object):
    def __init__(self):
        events.onBattleStart(self.onBattleStart)
        events.onBattleQuit(self.onBattleQuit)
        events.onReceiveShellInfo(self.onReceiveShellInfo)

        self.manager = UnderwaterHitsManager()

    def onBattleStart(self, *args):
        self._underwaterHits = {}
        self.manager.init()

    def onBattleQuit(self, *args):
        self._underwaterHits.clear()
        self.manager.kill()

    def onReceiveShellInfo(self, victimId, shooterId, ammoId, matId, shotId, hitType, damage, shotPosition, yaw, hlinfo):
        isUnderwater = hitType & 4
        isIncomingDamage = hitType & 0b1
        
        if isUnderwater:
            data = self._createHitData(isIncomingDamage, damage)
            self.manager.addEntity(data)

    def _createHitData(self, isIncomingDamage, damage):
        return dict(
            isIncomingDamage=isIncomingDamage,
            damage=damage,
            createdAt=utils.getTimeFromGameStart(),
        )
    

class UnderwaterHitsManager(object):
    def __init__(self):
        self._entities = []

    def addEntity(self, hitData):
        uwHit = UnderwaterHit(hitData)
        uwHit.callback = callbacks.callback(DISPLAY_TIME, self.removeEntity, uwHit)
        self._entities.append(uwHit)

        self.updateEntityList()

    def removeEntity(self, entity):
        self._entities.remove(entity)
        self.updateEntityList()
        callbacks.cancel(entity.callback)
        entity.kill()

    def updateEntityList(self):
        ui.updateUiElementData(self.managerEntityId, {'underwaterHitEntityIds': [i.entityId for i in self._entities]})

    def init(self, *args):
        self.managerEntityId = ui.createUiElement()
        ui.addDataComponentWithId(self.managerEntityId, COMPONENT_KEY, {'underwaterHitEntityIds': []})

    def kill(self, *args):
        for entity in self._entities:
            callbacks.cancel(entity.callback)
            entity.kill()
        self._entities = []
        ui.deleteUiElement(self.managerEntityId)

    
class UnderwaterHit(object):
    def __init__(self, hitData):
        self.callback = None

        self.entityId = ui.createUiElement()
        ui.addDataComponent(self.entityId, hitData)

    def kill(self, *args):
        self.callback = None
        ui.deleteUiElement(self.entityId)

underwaterHitViewer = UnderwaterHitViewer()
