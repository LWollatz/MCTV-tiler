points = [1,3,2,6,2,7,8,5,6,4,6,4,6,4,5,4,6,4,4,4,4,4,4,5,6,6,7,0,5,5]
points.sort()
print len(points)
print int(0.1*len(points)), int(0.9*len(points))
print points[int(0.1*len(points))], points[int(0.9*len(points))]

counts = [[x,points.count(x)] for x in points]
print counts
