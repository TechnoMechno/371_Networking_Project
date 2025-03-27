import pygame
import json

# Assume 'cookies' is your current state of cookies received from the server
# and send_message is your function to send a JSON message to the server.

def find_top_cookie(mouse_pos, cookies):
    """
    Given the current mouse position and the dictionary of cookie states,
    returns the ID of the topmost cookie (if any) under the cursor.
    
    Parameters:
      mouse_pos (tuple): The (x, y) position of the mouse.
      cookies (dict): Dictionary of cookies. Each value is expected to be a dict 
                      containing at least "position" (list or tuple) and "radius" (int).
    
    Returns:
      The cookie_id of the topmost cookie that the mouse is over, or None if none.
    """
    # Sort cookie IDs descending, assuming higher cookie_id means the cookie is on top.
    for cookie_id in sorted(cookies.keys(), reverse=True):
        cookie = cookies[cookie_id]
        pos = cookie["position"]  # e.g. [x, y]
        radius = cookie.get("radius", 30)  # default radius if not provided
        dx = mouse_pos[0] - pos[0]
        dy = mouse_pos[1] - pos[1]
        distance = (dx*dx + dy*dy) ** 0.5
        if distance < radius:
            return cookie_id
    return None

for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.MOUSEMOTION:
        # Always send the current mouse position
        mouse_pos = pygame.mouse.get_pos()
        # Here you might want to send a unified update message,
        # if not dragging any cookie, you set dragged_cookie to None.
        update_msg = {
            "type": "update",
            "position": mouse_pos,
            "dragged_cookie": None  # default when not dragging
        }
        send_message(update_msg)
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        top_cookie = find_top_cookie(mouse_pos, cookies)
        # Prepare the update message with the dragged cookie
        update_msg = {
            "type": "update",
            "position": mouse_pos,
            "dragged_cookie": top_cookie  # Could be None if no cookie is under the cursor
        }
        send_message(update_msg)
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        # When the mouse is released, no cookie is being dragged
        update_msg = {
            "type": "update",
            "position": mouse_pos,
            "dragged_cookie": None
        }
        send_message(update_msg)