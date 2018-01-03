var pools_url = $('#api_url').attr('data-url') + '?limit=1000';
pools_url = 'https://nodes.wlan-si.net/api/v2/pool/ip/?limit=1000';
var pools_array = [];
window.topLevelPools = [];
window.pools = {};

/**
 * Loads the results into an array until we get to the end of next url
 * @param a array into which the data gets loaded
 * @param url which to load
*/
function loadData(a, url) {
    $.getJSON( url, function( data ) {
        a = a.concat(data['results']);
        if (data['next'] !== null) {
            loadData(a, data['next']);
        }
        else{
            buildTree(a);
        }
    });
}

/**
 * Arranges the pools in the array into a tree
 * @param a Array of pools
 */
function buildTree(a) {
    //Map each pool to id
    a.forEach(function (pool) {
        pools[pool['@id']] = new Pool(pool['@id'], pool['network'], pool['prefix_length'], null, pool['description']);
    });
    //Add each pool to a parent pool
    a.forEach(function (pool) {
        if (pool['@id'] === pool['top_level']['@id']) {
            pools[pool['@id']].isTopLevel = true;
            topLevelPools.push(pools[pool['@id']]);
        }else{
            pools[pool['top_level']['@id']].addSubnet(pools[pool['@id']]);
            pools[pool['@id']].parent = pools[pool['top_level']['@id']];
        }
    });
}

loadData(pools_array, pools_url);