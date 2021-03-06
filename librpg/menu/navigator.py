import math

from librpg.locals import UP, DOWN, RIGHT, LEFT 


class WidgetNavigator(object):

    """
    A WidgetNavigator is an algorithm to decide which widget is reached
    when going towards a direction, starting at a widget. This defines a
    Cursor's behavior when controlled by the keyboard.
    """

    def find(self, widget, direction):
        """
        *Abstract.*

        Return the widget reached when going towards *direction* from *widget*.

        Return None if there is no other widget in that direction.
        """
        raise NotImplementedError('WidgetNavigator.find() is abstract')

    def enter_div(self, div, direction):
        """
        *Abstract.*

        Return the widget reached when a *div* is entered towards *direction*.

        Return None if the *div* should be skipped.
        """
        raise NotImplementedError('WidgetNavigator.enter_div() is abstract')


class DistanceNavigator(WidgetNavigator):

    """
    An abstract WidgetNavigator that calculates the distance between
    the starting widget and all others in the menu, and navigates to
    the one nearest.
    """

    MAX_DIST = 999999

    def find(self, widget, direction):
        #print '-' * 60
        #print 'find(%s, %d)' % (widget, direction)
        if widget.parent is None:
            return None

        width = widget.menu.width
        height = widget.menu.height

        best = None, DistanceNavigator.MAX_DIST
        for bound_widget in widget.menu.all_widgets:
            if (bound_widget.focusable
                and bound_widget is not widget):
                dist = self.calc_distance(widget,
                                          bound_widget,
                                          direction,
                                          width,
                                          height)
                #print 'comparing to %s = dist %d' % (bound_widget, dist)
                if dist < best[1]:
                    best = bound_widget, dist
        return best[0]

    def calc_distance(self, start, end, direction, width, height):
        """
        *Abstract.*

        Return the distance between *start* and *end* widgets, going
        from *start* towards *direction* in a menu with dimensions
        *width* x *height*.

        Return DistanceNavigator.MAX_DIST if *end* should not be reached.
        """
        raise NotImplementedError('DistanceNavigator.calc_distance() is '
                                  'abstract')

    def inside_angle(self, dy, dx, direction):
        if direction == UP:
            return dx <= dy
        elif direction == DOWN:
            return dx <= dy
        elif direction == RIGHT:
            return dy <= dx
        elif direction == LEFT:
            return dy <= dx

    def modulus_distance(self, start, end, n, direction=None):
        """
        Calculate the distance from start to end in a modulus n space.
        """
        if direction is None:
            r = abs(end - start)
            if r > n / 2:
                return n - r
            else:
                return r
        else:
            if direction == RIGHT or direction == DOWN:
                if end < start:
                    return n + end - start
                else:
                    return end - start
            else:
                if end < start:
                    return start - end
                else:
                    return n + start - end

    def modulus_point_distance(self, start, end, width, height, direction):
        x_dir, y_dir = self.get_xy_directions(direction)
        dx = self.modulus_distance(start[0], end[0], width, x_dir)
        dy = self.modulus_distance(start[1], end[1], height, y_dir)
        if not self.inside_angle(dy, dx, direction):
            #print 'dx ? y ? not inside angle'
            return None, None
        else:
            #print 'dx %d, dy %d' % (dx, dy)
            return dx, dy

    def get_xy_directions(self, direction):
        if direction == UP:
            x_dir = None
            y_dir = UP
        elif direction == DOWN:
            x_dir = None
            y_dir = DOWN
        elif direction == RIGHT:
            x_dir = RIGHT
            y_dir = None
        elif direction == LEFT:
            x_dir = LEFT
            y_dir = None
        return x_dir, y_dir


class EuclidianNavigator(DistanceNavigator):

    """
    A DistanceNavigator that uses the distance between the centers of the
    widgets as cost function.
    """

    def calc_distance(self, start, end, direction, width, height):
        start_center = start.get_center()
        end_center = end.get_center()
        if direction == UP:
            dy = self.modulus_distance(start_center[1], end_center[1], height,
                                       direction)
            dx = self.modulus_distance(start_center[0], end_center[0], width)
        elif direction == DOWN:
            dy = self.modulus_distance(start_center[1], end_center[1], height,
                                       direction)
            dx = self.modulus_distance(start_center[0], end_center[0], width)
        elif direction == RIGHT:
            dx = self.modulus_distance(start_center[0], end_center[0], width,
                                       direction)
            dy = self.modulus_distance(start_center[1], end_center[1], height)
        elif direction == LEFT:
            dx = self.modulus_distance(start_center[0], end_center[0], width,
                                       direction)
            dy = self.modulus_distance(start_center[1], end_center[1], height)
        #print 'dx %d, dy %d' % (dx, dy)
        if not self.inside_angle(dy, dx, direction):
            return DistanceNavigator.MAX_DIST
        else:
            return math.sqrt(dx ** 2 + dy ** 2)


class LineNavigator(DistanceNavigator):

    """
    A DistanceNavigator that uses the distance between the skeletons
    of the widgets as cost function. A Widget's skeleton is the line
    segment that is farthest from its borders.
    """

    HORIZONTAL = 1
    VERTICAL = 2
    POINT = 3

    def calc_distance(self, start, end, direction, width, height):
        start_axis, start1, start2 = self.calc_skeleton(start)
        _, end1, end2 = self.calc_skeleton(end)

        d = [None] * 4
        d[0] = self.perpedicular_distance(start1, start2, start_axis, end1,
                                          width, height, direction)
        #if d[0] is not None: print 'd[0] %d' % d[0]
        d[1] = self.perpedicular_distance(start1, start2, start_axis, end2,
                                          width, height, direction)
        #if d[1] is not None: print 'd[1] %d' % d[1]

        record = DistanceNavigator.MAX_DIST
        for i in xrange(4):
            if d[i] is None:
                continue
            new_dist = d[i]
            if new_dist < record:
                record = new_dist

        if record == DistanceNavigator.MAX_DIST:
            #print 'Need diagonals'
            dx, dy = [], []
            if start_axis == self.HORIZONTAL:
                if direction == UP or direction == DOWN:
                    x1, y1 = self.modulus_point_distance(start.get_center(),
                                                         end1, width, height,
                                                         direction)
                    x2, y2 = self.modulus_point_distance(start.get_center(),
                                                         end2, width, height,
                                                         direction)
                elif direction == LEFT:
                    x1, y1 = self.modulus_point_distance(start1, end1, width,
                                                         height, direction)
                    x2, y2 = self.modulus_point_distance(start1, end2, width,
                                                         height, direction)
                else:
                    x1, y1 = self.modulus_point_distance(start2, end1, width,
                                                         height,
                                                         direction)
                    x2, y2 = self.modulus_point_distance(start2, end2, width,
                                                         height, direction)
            elif start_axis == self.VERTICAL:
                if direction == LEFT or direction == RIGHT:
                    x1, y1 = self.modulus_point_distance(start.get_center(),
                                                         end1, width, height,
                                                         direction)
                    x2, y2 = self.modulus_point_distance(start.get_center(),
                                                         end2, width, height,
                                                         direction)
                elif direction == UP:
                    x1, y1 = self.modulus_point_distance(start1, end1, width,
                                                         height, direction)
                    x2, y2 = self.modulus_point_distance(start1, end2, width,
                                                         height, direction)
                else:
                    x1, y1 = self.modulus_point_distance(start2, end1, width,
                                                         height, direction)
                    x2, y2 = self.modulus_point_distance(start2, end2, width,
                                                         height, direction)
            else:
                    x1, y1 = self.modulus_point_distance(start1, end1, width,
                                                         height, direction)
                    x2, y2 = self.modulus_point_distance(start1, end2, width,
                                                         height, direction)
            dx.append(x1)
            dy.append(y1)
            dx.append(x2)
            dy.append(y2)
            for x, y in zip(dx, dy):
                if x is None or y is None:
                    continue
                new_dist = self.dist(x, y)
                if new_dist < record:
                    record = new_dist

        #print start, end
        #print 'dist(%s and %s) => r %s'\
        # % (str((start1, start2)), str((end1, end2)), str(record))
        return record

    def calc_skeleton(self, widget):
        center = widget.get_center()
        if widget.width < widget.height:
            offset = widget.width / 2
            start_y = widget.get_menu_position()[1] + offset
            end_y = widget.get_menu_position()[1] + widget.height - offset
            return (self.VERTICAL,
                    (center[0], start_y),
                    (center[0], end_y))
        elif widget.width > widget.height:
            offset = widget.height / 2
            start_x = widget.get_menu_position()[0] + offset
            end_x = widget.get_menu_position()[0] + widget.width - offset
            return (self.HORIZONTAL,
                    (start_x, center[1]),
                    (end_x, center[1]))
        else:
            return (self.POINT,
                    center,
                    center)

    def perpedicular_distance(self, start, end, axis, target, width, height,
                              direction):
        dir_x, dir_y = self.get_xy_directions(direction)
        if axis == self.VERTICAL\
           and (direction == LEFT or direction == RIGHT):
            if start[1] <= target[1] and target[1] < end[1]:
                return self.modulus_distance(start[0], target[0], height,
                                             dir_x)
        elif axis == self.HORIZONTAL\
             and (direction == UP or direction == DOWN):
            if start[0] <= target[0] and target[0] < end[0]:
                return self.modulus_distance(start[1], target[1], width, dir_y)
        return None

    def modulus_distance(self, start, end, n, direction=None):
        WRAP_WEIGHT = 2.0
        if direction is None:
            r = abs(end - start)
            alt = WRAP_WEIGHT * (n - r)
            return min(alt, r)
        else:
            if direction == RIGHT or direction == DOWN:
                if end < start:
                    return WRAP_WEIGHT * (n + end - start)
                else:
                    return end - start
            else:
                if end < start:
                    return start - end
                else:
                    return WRAP_WEIGHT * (n + start - end)

    def dist(self, dx, dy):
        return dx + dy


class WidgetGateway(object):

    def __init__(self, widget, up=None, right=None, down=None, left=None):
        self.widget = widget
        self.up = up
        self.right = right
        self.down = down
        self.left = left

    def build_map(self):
        self.direction_map = {UP: self.up,
                              RIGHT: self.right,
                              DOWN: self.down,
                              LEFT: self.left}
        #print 'MAP %s %s' % (self.widget, self.direction_map)

    def crystallize(self, widget_navigator=None):
        if widget_navigator is None:
            widget_navigator = LineNavigator()
        self.up = widget_navigator.find(self.widget, UP)
        self.right = widget_navigator.find(self.widget, RIGHT)
        self.down = widget_navigator.find(self.widget, DOWN)
        self.left = widget_navigator.find(self.widget, LEFT)
        self.widget.crystallized = True
        self.build_map()

    def step(self, direction, widget_navigator=None):
        if self.widget.crystallized:
            target = self.direction_map.get(direction, None)
        else:
            if widget_navigator is None:
                widget_navigator = LineNavigator()
            target = widget_navigator.find(self.widget, direction)
        return target
