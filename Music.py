import pygame


class Songs:
    introPath = 'music/INTRO.mp3'

    stonePath = 'music/STONE_SPEEDING_UP.mp3'
    stonePathLoop = 'music/STONE_FAST.mp3'
    STNEXT = pygame.USEREVENT + 1

    ironPath = 'music/IRON_SPEEDING_UP.mp3'
    ironPathLoop = 'music/IRON_FAST.mp3'
    INEXT = pygame.USEREVENT + 2

    medPath = 'music/MEDIEVAL_SPEEDING_UP.mp3'
    medPathLoop = 'music/MEDIEVAL_FAST.mp3'
    MENEXT = pygame.USEREVENT + 3

    mhPath = 'music/MODERN_HISTORY_SPEEDING_UP.mp3'
    mhPathLoop = 'music/MODERN_HISTORY_FAST.mp3'
    MHNEXT = pygame.USEREVENT + 4

    maPath = 'music/MODERN_AGE_SPEEDING_UP.mp3'
    maPathLoop = 'music/MODERN_AGE_FAST.mp3'
    MANEXT = pygame.USEREVENT + 5

    spacePath = 'music/SPACE_SPEEDING_UP.mp3'
    spacePathLoop = 'music/SPACE_FAST.mp3'
    SPNEXT = pygame.USEREVENT + 6


def play(songNum):
    if songNum == -1:
        playIntro()
    if songNum == 0:
        playStone()
    if songNum == 1:
        playIron()
    if songNum == 2:
        playMed()
    if songNum == 3:
        playMh()
    if songNum == 4:
        playMa()
    if songNum == 5:
        playSpace()


# Intro
def playIntro():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.introPath)
    pygame.mixer.music.play(-1)


# Stone
def playStone():
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.stonePath)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(Songs.STNEXT)


def playStoneLoop():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.stonePathLoop)
    pygame.mixer.music.play(-1)


# Iron
def playIron():
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.ironPath)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(Songs.INEXT)


def playIronLoop():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.ironPathLoop)
    pygame.mixer.music.play(-1)


# Medieval
def playMed():
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.medPath)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(Songs.MENEXT)


def playMedLoop():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.medPathLoop)
    pygame.mixer.music.play(-1)


# Modern History
def playMh():
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.mhPath)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(Songs.MHNEXT)


def playMhLoop():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.mhPathLoop)
    pygame.mixer.music.play(-1)


# Modern
def playMa():
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.maPath)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(Songs.MANEXT)


def playMaLoop():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.maPathLoop)
    pygame.mixer.music.play(-1)


# Space
def playSpace():
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.spacePath)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(Songs.SPNEXT)


def playSpaceLoop():
    pygame.mixer.quit()
    pygame.mixer.init()
    pygame.mixer.music.load(Songs.spacePathLoop)
    pygame.mixer.music.play(-1)
