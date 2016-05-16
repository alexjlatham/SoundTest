import sys

def est_variance(vals):
    mean = float(sum(vals))/float(len(vals))
    var = 0
    for i in range(len(vals)):
        var += (vals[i] - mean)**2
    var*= 1./(len(vals)-1)

    print "Mean: ", str(mean)
    print "Estimated variance: ", str(var)
    print "Estimated standard dev: ", str(var**.5)
    return var

if __name__ == "__main__":
    vals = str(raw_input('Enter a list of values: '))
    vals = vals.replace(',', ' ')
    vals = vals.split()
    try:
        vals = [int(x) for x in vals]
        est_variance(vals)
    except ValueError:
        print "This is for use with numbers."


