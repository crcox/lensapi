import re

class ScriptWriter:
    def __init__(self, f, jdata, indentchar='\t'):
        def parse_jdata(x):
            # If any of the networkObjects values contain strings, they need to
            # be handled and evaluated to a numeric value.
            valid_operators = ('+','-','*','/')
            NO = x['networkObjects']
            pat = r"([a-zA-Z_]+)"
            rep = r"NO['\1']"
            for k,v in NO.items():
                if isinstance(v, str) or isinstance(v, unicode):
                    eq = re.sub(pat, rep, v)
                    x['networkObjects'][k] = eval(eq)

            return x

        self.f=f
        self.jdata=parse_jdata(jdata)
        self.indent=0
        self.indentchar=indentchar
        self.mainline = ''
        self.closeline = ''

    def __enter__(self):
        INDENT = self.indent * self.indentchar
        self.f.write('{i}{m}\n'.format(i=INDENT,m=self.mainline))
        self.indent += 1
        return self

    def __exit__(self, *args):
        self.indent -= 1
        INDENT = self.indent * self.indentchar
        self.f.write('{i}}}\n'.format(i=INDENT))

    def while_(self, stoppingCriterion):
        self.mainline = 'while {{$Test(percentCorrect) < {crit}}} {{'.format(
            crit=stoppingCriterion
        )
        return self

    def for_(self,var, init, limit):
        self.mainline = 'for {{set {i} {init}}} {{${i} <= {limit}}} {{incr {i}}} {{'.format(
            i=var,
            limit=limit,
            init=init
        )
        return self

    def if_(self, condition):
        self.mainline = 'if {{{cond}}} {{'.format(
            cond=condition
        )
        return self

    def elseif_(self, condition):
        self.mainline = 'elseif {{{cond}}} {{'.format(
            cond=condition
        )
        return self

    def else_(self):
        self.mainline = 'else {'
        return self

    def setVar(self,variable,value):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}set {variable} {value}\n'.format(
            indent=INDENT,
            variable=variable,
            value=value
            )
        )

    def setObj(self,objectAndField,value):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}setObject {obj} {value}\n'.format(
            indent=INDENT,
            obj=objectAndField,
            value=value
            )
        )

    def source(self, pathToScript):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}source "{path}"\n'.format(
            indent=INDENT,
            path=pathToScript
            )
        )

    def resetNet(self):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}resetNet\n'.format(
            indent=INDENT
            )
        )

    def loadWeights(self, pathToWeights):
        INDENT = self.indent * self.indentchar
        tclstr = '{indent}loadWeights {path}\n'.format(
            indent=INDENT,
            path=pathToWeights
        )
        try:
            self.f.write(tclstr)
        except AttributeError:
            return tclstr

    def loadExamples(self, path, mode):
        INDENT = self.indent * self.indentchar
        if path[0] in ['[','"']:
            fmtstr = '{indent}loadExamples {path} -exmode {mode}\n'
        else:
            fmtstr = '{indent}loadExamples "{path}" -exmode {mode}\n'

        self.f.write(fmtstr.format(
            indent=INDENT,
            path=path,
            mode=mode
            )
        )

    def useTrainingSet(self, setName):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}useTrainingSet {name}\n'.format(
            indent=INDENT,
            name=setName
            )
        )

    def useTestingSet(self, setName):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}useTestingSet {name}\n'.format(
            indent=INDENT,
            name=setName
            )
        )

    def testErrAccRT(self, fhandle, groups=0):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}testErrAccRT ${f} {g}\n'.format(
            indent=INDENT,
            f=fhandle,
            g=groups
            )
        )

    def test(self):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}test\n'.format(
            indent=INDENT
            )
        )

    def train(self, algorithm):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}train -a {alg}\n'.format(
            indent=INDENT,
            alg=algorithm
            )
        )

    def writeFrontMatter(self):
        from textwrap import wrap
        msg = "This script was automatically generated using the json2trainScript function in the aae module. This script should be run from the root of an experiment folder, which will have sub-folders for individual runs of the experiment (00/, 01/, etc) and a folder for example files (ex/). Lens .in files should be in the root directory, as well. The subfolder for each run should have a folder for weights. Error, accuracy, and activation values will be written into separate files within the directory for each run."
        msg = wrap(msg, width=70, initial_indent="# ", subsequent_indent="# ")
        for line in msg:
            self.f.write(line+'\n')

    def openNetOutputFile(self, filename, binary, append):
        INDENT = self.indent * self.indentchar
        if binary == True and append == True:
            fmtstr = '{indent}openNetOutputFile {filename} -binary -append\n'
        elif binary == True and append == False:
            fmtstr = '{indent}openNetOutputFile {filename} -binary\n'
        elif binary == False and append == True:
            fmtstr = '{indent}openNetOutputFile {filename} -append\n'
        else:
            fmtstr = '{indent}openNetOutputFile {filename}\n'

        self.f.write(fmtstr.format(indent=INDENT,filename=filename))

    def closeNetOutputFile(self):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}closeNetOutputFile\n'.format(indent=INDENT))

    def openFileConnection(self, path, handle, method):
        INDENT = self.indent * self.indentchar
        if path[0] in ['[','"']:
            fmtstr = '{indent}set {handle} [open {path} {method}]\n'
        else:
            fmtstr = '{indent}set {handle} [open "{path}" {method}]\n'

        self.f.write(fmtstr.format(
            indent=INDENT,
            handle=handle,
            path=path,
            method=method
            )
        )
        return handle

    def closeFileConnection(self, handle):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}close ${handle}\n'.format(
            indent=INDENT,
            handle=handle
            )
        )

    def writeHeading(self, heading):
        rule = "#" * 80
        self.f.write('\n')
        self.f.write('{rule}\n'.format(rule=rule))
        self.f.write('# {heading: ^76} #\n'.format(heading=heading))
        self.f.write('{rule}\n'.format(rule=rule))

    def writeError(self, handle):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}puts ${handle} "[format "%.2f" $Test(totalError)] "\n'.format(
            indent=INDENT,
            handle="errlog"
            )
        )

    def writeAccuracy(self, handle):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}puts ${handle} "[format "%.2f" $Test(percentCorrect)] "\n'.format(
            indent=INDENT,
            handle="acclog"
            )
        )

    def saveWeights(self,pathToWeights):
        INDENT = self.indent * self.indentchar
        tclstr = '{indent}saveWeights {path}\n'.format(indent=INDENT,path=pathToWeights)
        try:
            self.f.write(tclstr)
        except AttributeError:
            return tclstr

    def writeNewline(self, handle):
        INDENT = self.indent * self.indentchar
        self.f.write('{indent}puts ${handle} ""\n'.format(
            indent=INDENT,
            handle=handle
            )
        )
