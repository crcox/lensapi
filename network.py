def writeNetworkDefinition(jdat,f):
    f.write('addNet {name:s} -i {intervals:d} -t {ticks:d} {netType:s}\n'.format(
        name=jdat.get('name'),
        intervals=jdat.get('intervals'),
        ticks=jdat.get('ticksPerInterval'),
        netType=jdat.get('netType')
        ))

def writeLayerDefinitions(jdat,f):
    for key, attr in jdat['layers'].items():
        line = 'addGroup {layerName:s} {nunits:d}'.format(
                layerName=key,
                nunits=attr.get('nunits')
                )
        if attr['type'] == 'INPUT':
            line = line + ' {layerType:s}'.format(
                    layerType=attr.get('type').upper()
                    )
        elif attr['type'] == 'OUTPUT':
            line = line + ' {layerType:s} {errType:s}'.format(
                    layerType=attr.get('type').upper(),
                    errType=attr.get('errorType','CROSS_ENTROPY')
                    )
            if attr.get('biased',True):
                line = line + ' +BIASED'
            else:
                line = line + ' -BIASED'
        elif attr['type'] == 'HIDDEN':
            if attr.get('biased',True):
                line = line + ' +BIASED'
            else:
                line = line + ' -BIASED'
        f.write(line+'\n');

def writeConnectivityDefinitions(jdat,f):
    for attr in jdat['connections']:
        attr['weights'] = attr.get('weights',{})
        line = 'connectGroups ' + ' '.join(attr.get('pattern'))
        line = line + ' -projection {pType:s} -mean {mean:d} -range {range:d}'.format(
                pType=attr.get('projection','FULL'),
                mean=attr['weights'].get('mean',0),
                range=attr['weights'].get('range',1)
                )
        if attr['weights'].get('bidirectional',False):
            line = line + ' -bidirectional'
        f.write(line+'\n')
