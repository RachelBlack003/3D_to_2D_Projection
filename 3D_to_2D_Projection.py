import pygame, math, torch

class ObjectList:
    def __init__(self):
        self.list = []
    def append(self,x,y,z,color):
        self.list.append([torch.tensor([[x,y,z]]), color])

class Camera:
    def __init__(self):
        self.pos = torch.tensor([0.,0.,0.])
        self.rot = 0
        self.movingTo = torch.tensor([0.,0.,0.])
        self.rotatingTo = 0

    def update(self):
        '''
        Update is called every frame to update the position and rotation of the camera.
        '''
        self.rot = (self.rot + self.rotatingTo)%(2*math.pi)
        self.pos.add_(AdjustRotationForCamera(self.movingTo).reshape(3))



def Render(tensor, color):
    '''
    Render goes through other functions and modifies the given tensor to be
    able to project it onto a 2D plane.
    '''
    tensor = AdjustPos(tensor)
    tensor = AdjustRotation(tensor)
    if tensor[2] <= 0: #Object only renders if node is in front of the camera.
        return -1
    
    tensor = ScaleForWindow(tensor)

    Draw(tensor, color)

    return 0

def AdjustPos(tensor):
    '''
    Subtracts the camera position from the objects position to get the object relative to
    the camera.
    '''
    tensor = tensor.sub(camera.pos)

    return tensor

def AdjustRotation(tensor):
    '''
    Uses the rotation matrix [cos(theta), 0, -sin(theta)]
                             [     0,     1,      0     ]
                             [sin(theta), 0,  cos(theta)]
    to rotate the nodes around the camera according to theta (camera.rot). This is
    so that objects can be projects onto a 2D plane according to x and y, with
    z later being used to simulate perspective, as the objects are rotated so that
    the z axis is 'aligned' with the camera.
    '''
    CurRotation = torch.tensor([[math.cos(camera.rot), 0., -math.sin(camera.rot)],
                                [0.                  , 1., 0.],
                                [math.sin(camera.rot), 0., math.cos(camera.rot)]])
    tensor = torch.mm(CurRotation, tensor.reshape([3,1]))

    return tensor

def AdjustRotationForCamera(tensor):
    '''
    Slightly modified AdjustRotation function so that the camera rotation affects where
    the camera moves when wasd is pressed. That way, pressing 'w' always makes it
    feel like you are moving forward.
    '''
    CurRotation = torch.tensor([[math.cos(-camera.rot), 0., -math.sin(-camera.rot)],
                                [0.                   , 1., 0.],
                                [math.sin(-camera.rot), 0., math.cos(-camera.rot)]])
    tensor = torch.mm(CurRotation, tensor.reshape([3,1]))

    return tensor


def ScaleForWindow(tensor):
    '''
    This function takes the x and y values (tensor[0] and tensor[1]) and divides it 
    by the z value (tensor[2]).
    It then multiplies both values by 400 to make them fit well into the screen.
    400 and 300 are subtracted from x and y to center the points on the screen because
    (0,0) in pygame is the top right corner. That is also the reason y is multiplied by
    -1 because it would be displayed as the inverse from the coordinates otherwise.
    '''
    tensor[0] = (tensor[0]/tensor[2])* 400 + 400
    tensor[1] = -(tensor[1]/tensor[2])* 400 + 300
    return tensor


def Draw(tensor, color):
    """draw the node to the screen"""
    pygame.draw.circle(screen, color, (int(tensor[0]), int(tensor[1])), int(6/tensor[2]))

winwidth = 800  # width of window
winheight = 600  # height of window
background = (20, 5, 35)  # this is close to black

screen = pygame.display.set_mode((winwidth, winheight))
clock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("3D Game")
pygame.event.set_allowed([pygame.QUIT, pygame.KEYUP, pygame.KEYDOWN])

screen.fill(background)


quit = False
moveSpeed = 0.015
turnSpeed = 0.03

#myList is an object that contains all of the nodes to be rendered.
myList = ObjectList()
camera = Camera()


myList.append(0.2,0.2,1., "red")
myList.append(0.2,0.2,1.4, "blue")
myList.append(-0.2,0.2,1, "green")
myList.append(-0.2,0.2,1.4, "yellow")

myList.append(0.2,-0.2,1, "white")
myList.append(0.2,-0.2,1.4, "orange")
myList.append(-0.2,-0.2,1, "cyan")
myList.append(-0.2,-0.2,1.4, "purple")

while not quit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
            break
        #Sequence of if statements detect movement inputs from user.
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                quit = True
                break
            elif event.key == pygame.K_s:
                camera.movingTo[2] -= moveSpeed
            elif event.key == pygame.K_w:
                camera.movingTo[2] += moveSpeed
            elif event.key == pygame.K_a:
                camera.movingTo[0] -= moveSpeed
            elif event.key == pygame.K_d:
                camera.movingTo[0] += moveSpeed
            elif event.key == pygame.K_RIGHT:
                camera.rotatingTo += turnSpeed
            elif event.key == pygame.K_LEFT:
                camera.rotatingTo -= turnSpeed
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                camera.movingTo[2] += moveSpeed
            elif event.key == pygame.K_w:
                camera.movingTo[2] -= moveSpeed
            elif event.key == pygame.K_a:
                camera.movingTo[0] += moveSpeed
            elif event.key == pygame.K_d:
                camera.movingTo[0] -= moveSpeed
            elif event.key == pygame.K_RIGHT:
                camera.rotatingTo -= turnSpeed
            elif event.key == pygame.K_LEFT:
                camera.rotatingTo += turnSpeed

    camera.update() #Applies movements inputed to the camera object.

    screen.fill(background)

    if quit:
        break
    #renders all of the objects in myList
    for i in myList.list:
        Render(i[0], i[1])


    clock.tick(60)
    pygame.display.flip()

pygame.quit()