def writeNetworkDefinition(jdat,f):
    f.write('addNet {name:s} -i {intervals:d} -t {ticks:d} {netType:s}\n'.format(
        name=jdat.get('name'),
        intervals=jdat.get('intervals'),
        ticks=jdat.get('ticksPerInterval'),
        netType=jdat.get('netType')
        ))

def writeLayerDefinitions(jdat,f):
    for layer in jdat['layers']:
        line = 'addGroup {layerName:s} {nunits:d}'.format(
                layerName=layer['name'],
                nunits=layer['nunits']
                )
        if layer['type'] == 'INPUT':
            line = line + ' {layerType:s}'.format(
                    layerType=layer['type'].upper()
                    )
        elif layer['type'] == 'OUTPUT':
            line = line + ' {layerType:s} {errType:s}'.format(
                    layerType=layer.get('type').upper(),
                    errType=layer.get('errorType','CROSS_ENTROPY')
                    )
            if layer.get('biased',True):
                line = line + ' +BIASED'
            else:
                line = line + ' -BIASED'
        elif layer['type'] == 'HIDDEN':
            if layer.get('biased',True):
                line = line + ' +BIASED'
            else:
                line = line + ' -BIASED'
        try:
            if layer['useHistory']:
                line = line + ' USE_OUTPUT_HIST'
                if layer['type'] == 'OUTPUT':
                    line = line + ' USE_TARGET_HIST'
        except KeyError:
            pass
        try:
            if layer['writeOutputs']:
                line = line + ' WRITE_OUTPUTS'
            else:
                line = line + ' -WRITE_OUTPUTS'
        except KeyError:
            pass

        f.write(line+'\n');

def writeConnectivityDefinitions(jdat,f):
    for attr in jdat['connections']:
        attr['weights'] = attr.get('weights',{})
	groups = ['{'+' '.join(y)+'}' if isinstance(y, list) else y for y in attr.get('pattern')]
        line = 'connectGroups ' + ' '.join(groups)
        line = line + ' -projection {pType:s} -mean {mean:d} -range {range:d}'.format(
                pType=attr.get('projection','FULL'),
                mean=attr['weights'].get('mean',0),
                range=attr['weights'].get('range',1)
                )
        if attr['weights'].get('bidirectional',False):
            line = line + ' -bidirectional'
	strength = attr['weights'].get('strength',False):
        if strength:
            line = line + ' -s {s:0.4f}'.format(s=strength)
        f.write(line+'\n')
