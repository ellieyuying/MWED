"""
EVP 纯语言数据（词典、集合、正则常量），供正则生成器与预处理器导入。

  § 1  VERB_FORMS         动词变形正则 {原形: r'(?:变形1|变形2|...)'}
  § 2  INFLECTION_TO_BASE 变形→原形反查（从 _EXTRA_INFLECTIONS 构建）
  § 3  CONTRACTIONS       缩写展开表
  § 4  IRREG_VERB         不规则动词过去式/过去分词→原形
  § 5  代词归一集合        POSS_TO_YOUR / REFL_TO_YOURSELF / PRONOUN_TO_SB
  § 6  正则常量           _TIMEUNIT_RE / _NUM_RE / _DET / _SBPOS_RE
"""

# § 1  动词变形正则字典 VERB_FORMS：{原形: r'(?:变形1|变形2|...)'}
VERB_FORMS = {
    'be':         r'(?:be|is|are|was|were|been|being|am)',
    'do':         r'(?:do|does|did|done|doing)',
    'have':       r'(?:have|has|had|having)',
    'make':       r'(?:make|makes|made|making)',
    'get':        r'(?:get|gets|got|gotten|getting)',
    'take':       r'(?:take|takes|took|taken|taking)',
    'give':       r'(?:give|gives|gave|given|giving)',
    'go':         r'(?:go|goes|went|gone|going)',
    'come':       r'(?:come|comes|came|coming)',
    'see':        r'(?:see|sees|saw|seen|seeing)',
    'know':       r'(?:know|knows|knew|known|knowing)',
    'think':      r'(?:think|thinks|thought|thinking)',
    'feel':       r'(?:feel|feels|felt|feeling)',
    'say':        r'(?:say|says|said|saying)',
    'tell':       r'(?:tell|tells|told|telling)',
    'use':        r'(?:use|uses|used|using)',
    'find':       r'(?:find|finds|found|finding)',
    'put':        r'(?:put|puts|putting)',
    'set':        r'(?:set|sets|setting)',
    'keep':       r'(?:keep|keeps|kept|keeping)',
    'let':        r'(?:let|lets|letting)',
    'turn':       r'(?:turn|turns|turned|turning)',
    'bring':      r'(?:bring|brings|brought|bringing)',
    'call':       r'(?:call|calls|called|calling)',
    'try':        r'(?:try|tries|tried|trying)',
    'start':      r'(?:start|starts|started|starting)',
    'stop':       r'(?:stop|stops|stopped|stopping)',
    'follow':     r'(?:follow|follows|followed|following)',
    'work':       r'(?:work|works|worked|working)',
    'live':       r'(?:live|lives|lived|living)',
    'mean':       r'(?:mean|means|meant|meaning)',
    'change':     r'(?:change|changes|changed|changing)',
    'show':       r'(?:show|shows|showed|shown|showing)',
    'play':       r'(?:play|plays|played|playing)',
    'run':        r'(?:run|runs|ran|running)',
    'move':       r'(?:move|moves|moved|moving)',
    'hold':       r'(?:hold|holds|held|holding)',
    'happen':     r'(?:happen|happens|happened|happening)',
    'pay':        r'(?:pay|pays|paid|paying)',
    'fall':       r'(?:fall|falls|fell|fallen|falling)',
    'break':      r'(?:break|breaks|broke|broken|breaking)',
    'cut':        r'(?:cut|cuts|cutting)',
    'lose':       r'(?:lose|loses|lost|losing)',
    'ask':        r'(?:ask|asks|asked|asking)',
    'need':       r'(?:need|needs|needed|needing)',
    'leave':      r'(?:leave|leaves|left|leaving)',
    'learn':      r'(?:learn|learns|learned|learnt|learning)',
    'read':       r'(?:read|reads|reading)',
    'look':       r'(?:look|looks|looked|looking)',
    'stand':      r'(?:stand|stands|stood|standing)',
    'wait':       r'(?:wait|waits|waited|waiting)',
    'write':      r'(?:write|writes|wrote|written|writing)',
    'become':     r'(?:become|becomes|became|becoming)',
    'spend':      r'(?:spend|spends|spent|spending)',
    'grow':       r'(?:grow|grows|grew|grown|growing)',
    'open':       r'(?:open|opens|opened|opening)',
    'walk':       r'(?:walk|walks|walked|walking)',
    'win':        r'(?:win|wins|won|winning)',
    'buy':        r'(?:buy|buys|bought|buying)',
    'send':       r'(?:send|sends|sent|sending)',
    'build':      r'(?:build|builds|built|building)',
    'die':        r'(?:die|dies|died|dying)',
    'raise':      r'(?:raise|raises|raised|raising)',
    'pass':       r'(?:pass|passes|passed|passing)',
    'carry':      r'(?:carry|carries|carried|carrying)',
    'deal':       r'(?:deal|deals|dealt|dealing)',
    'drive':      r'(?:drive|drives|drove|driven|driving)',
    'hear':       r'(?:hear|hears|heard|hearing)',
    'sit':        r'(?:sit|sits|sat|sitting)',
    'meet':       r'(?:meet|meets|met|meeting)',
    'eat':        r'(?:eat|eats|ate|eaten|eating)',
    'lead':       r'(?:lead|leads|led|leading)',
    'speak':      r'(?:speak|speaks|spoke|spoken|speaking)',
    'wake':       r'(?:wake|wakes|woke|woken|waking)',
    'wear':       r'(?:wear|wears|wore|worn|wearing)',
    'wish':       r'(?:wish|wishes|wished|wishing)',
    'worry':      r'(?:worry|worries|worried|worrying)',
    'understand': r'(?:understand|understands|understood|understanding)',
    'choose':     r'(?:choose|chooses|chose|chosen|choosing)',
    'reach':      r'(?:reach|reaches|reached|reaching)',
    'add':        r'(?:add|adds|added|adding)',
    'act':        r'(?:act|acts|acted|acting)',
    'watch':      r'(?:watch|watches|watched|watching)',
    'suggest':    r'(?:suggest|suggests|suggested|suggesting)',
    'include':    r'(?:include|includes|included|including)',
    'forget':     r'(?:forget|forgets|forgot|forgotten|forgetting)',
    'allow':      r'(?:allow|allows|allowed|allowing)',
    'help':       r'(?:help|helps|helped|helping)',
    'expect':     r'(?:expect|expects|expected|expecting)',
    'like':       r'(?:like|likes|liked|liking)',
    'want':       r'(?:want|wants|wanted|wanting)',
    'aim':        r'(?:aim|aims|aimed|aiming)',
    'avoid':      r'(?:avoid|avoids|avoided|avoiding)',
    'appear':     r'(?:appear|appears|appeared|appearing)',
    'bear':       r'(?:bear|bears|bore|borne|bearing)',
    'begin':      r'(?:begin|begins|began|begun|beginning)',
    'bend':       r'(?:bend|bends|bent|bending)',
    'blow':       r'(?:blow|blows|blew|blown|blowing)',
    'burn':       r'(?:burn|burns|burned|burnt|burning)',
    'care':       r'(?:care|cares|cared|caring)',
    'catch':      r'(?:catch|catches|caught|catching)',
    'claim':      r'(?:claim|claims|claimed|claiming)',
    'climb':      r'(?:climb|climbs|climbed|climbing)',
    'count':      r'(?:count|counts|counted|counting)',
    'cover':      r'(?:cover|covers|covered|covering)',
    'cross':      r'(?:cross|crosses|crossed|crossing)',
    'dare':       r'(?:dare|dares|dared|daring)',
    'depend':     r'(?:depend|depends|depended|depending)',
    'dive':       r'(?:dive|dives|dived|dove|diving)',
    'doubt':      r'(?:doubt|doubts|doubted|doubting)',
    'drag':       r'(?:drag|drags|dragged|dragging)',
    'draw':       r'(?:draw|draws|drew|drawn|drawing)',
    'drop':       r'(?:drop|drops|dropped|dropping)',
    'end':        r'(?:end|ends|ended|ending)',
    'fade':       r'(?:fade|fades|faded|fading)',
    'fail':       r'(?:fail|fails|failed|failing)',
    'fill':       r'(?:fill|fills|filled|filling)',
    'finish':     r'(?:finish|finishes|finished|finishing)',
    'fit':        r'(?:fit|fits|fitted|fitting)',
    'fix':        r'(?:fix|fixes|fixed|fixing)',
    'focus':      r'(?:focus|focuses|focused|focusing)',
    'fold':       r'(?:fold|folds|folded|folding)',
    'gain':       r'(?:gain|gains|gained|gaining)',
    'grab':       r'(?:grab|grabs|grabbed|grabbing)',
    'grant':      r'(?:grant|grants|granted|granting)',
    'grip':       r'(?:grip|grips|gripped|gripping)',
    'guess':      r'(?:guess|guesses|guessed|guessing)',
    'hang':       r'(?:hang|hangs|hung|hanging)',
    'hope':       r'(?:hope|hopes|hoped|hoping)',
    'hurry':      r'(?:hurry|hurries|hurried|hurrying)',
    'join':       r'(?:join|joins|joined|joining)',
    'jump':       r'(?:jump|jumps|jumped|jumping)',
    'kick':       r'(?:kick|kicks|kicked|kicking)',
    'knock':      r'(?:knock|knocks|knocked|knocking)',
    'launch':     r'(?:launch|launches|launched|launching)',
    'lay':        r'(?:lay|lays|laid|laying)',
    'lean':       r'(?:lean|leans|leaned|leant|leaning)',
    'lie':        r'(?:lie|lies|lay|lain|lying)',
    'lift':       r'(?:lift|lifts|lifted|lifting)',
    'link':       r'(?:link|links|linked|linking)',
    'lock':       r'(?:lock|locks|locked|locking)',
    'love':       r'(?:love|loves|loved|loving)',
    'miss':       r'(?:miss|misses|missed|missing)',
    'name':       r'(?:name|names|named|naming)',
    'notice':     r'(?:notice|notices|noticed|noticing)',
    'offer':      r'(?:offer|offers|offered|offering)',
    'owe':        r'(?:owe|owes|owed|owing)',
    'own':        r'(?:own|owns|owned|owning)',
    'pick':       r'(?:pick|picks|picked|picking)',
    'plan':       r'(?:plan|plans|planned|planning)',
    'please':     r'(?:please|pleases|pleased|pleasing)',
    'pour':       r'(?:pour|pours|poured|pouring)',
    'press':      r'(?:press|presses|pressed|pressing)',
    'prove':      r'(?:prove|proves|proved|proven|proving)',
    'pull':       r'(?:pull|pulls|pulled|pulling)',
    'push':       r'(?:push|pushes|pushed|pushing)',
    'race':       r'(?:race|races|raced|racing)',
    'realize':    r'(?:realize|realizes|realized|realizing|realise|realises|realised|realising)',
    'refer':      r'(?:refer|refers|referred|referring)',
    'rely':       r'(?:rely|relies|relied|relying)',
    'remain':     r'(?:remain|remains|remained|remaining)',
    'rescue':     r'(?:rescue|rescues|rescued|rescuing)',
    'reveal':     r'(?:reveal|reveals|revealed|revealing)',
    'ring':       r'(?:ring|rings|rang|rung|ringing)',
    'rise':       r'(?:rise|rises|rose|risen|rising)',
    'roll':       r'(?:roll|rolls|rolled|rolling)',
    'rush':       r'(?:rush|rushes|rushed|rushing)',
    'scratch':    r'(?:scratch|scratches|scratched|scratching)',
    'seek':       r'(?:seek|seeks|sought|seeking)',
    'seem':       r'(?:seem|seems|seemed|seeming)',
    'sell':       r'(?:sell|sells|sold|selling)',
    'settle':     r'(?:settle|settles|settled|settling)',
    'shake':      r'(?:shake|shakes|shook|shaken|shaking)',
    'share':      r'(?:share|shares|shared|sharing)',
    'shed':       r'(?:shed|sheds|shedding)',
    'shut':       r'(?:shut|shuts|shutting)',
    'slide':      r'(?:slide|slides|slid|sliding)',
    'slip':       r'(?:slip|slips|slipped|slipping)',
    'snap':       r'(?:snap|snaps|snapped|snapping)',
    'spread':     r'(?:spread|spreads|spreading)',
    'spring':     r'(?:spring|springs|sprang|sprung|springing)',
    'stay':       r'(?:stay|stays|stayed|staying)',
    'step':       r'(?:step|steps|stepped|stepping)',
    'stick':      r'(?:stick|sticks|stuck|sticking)',
    'stretch':    r'(?:stretch|stretches|stretched|stretching)',
    'strike':     r'(?:strike|strikes|struck|striking)',
    'stumble':    r'(?:stumble|stumbles|stumbled|stumbling)',
    'sweep':      r'(?:sweep|sweeps|swept|sweeping)',
    'switch':     r'(?:switch|switches|switched|switching)',
    'talk':       r'(?:talk|talks|talked|talking)',
    'taste':      r'(?:taste|tastes|tasted|tasting)',
    'throw':      r'(?:throw|throws|threw|thrown|throwing)',
    'tie':        r'(?:tie|ties|tied|tying)',
    'touch':      r'(?:touch|touches|touched|touching)',
    'train':      r'(?:train|trains|trained|training)',
    'treat':      r'(?:treat|treats|treated|treating)',
    'trust':      r'(?:trust|trusts|trusted|trusting)',
    'twist':      r'(?:twist|twists|twisted|twisting)',
    'value':      r'(?:value|values|valued|valuing)',
    'visit':      r'(?:visit|visits|visited|visiting)',
    'wander':     r'(?:wander|wanders|wandered|wandering)',
    'wave':       r'(?:wave|waves|waved|waving)',
    'wipe':       r'(?:wipe|wipes|wiped|wiping)',
}


# ─────────────────────────────────────────────────────────────────
# § 2  变形→原形反向查找 INFLECTION_TO_BASE
# 由 _EXTRA_INFLECTIONS 自动构建，供 generator 和 matcher 预处理层兜底使用。
# ─────────────────────────────────────────────────────────────────

_EXTRA_INFLECTIONS = {
    'be':     ['is','are','was','were','been','being','am'],
    'do':     ['does','did','done','doing'],
    'have':   ['has','had','having'],
    'go':     ['goes','went','gone','going'],
    'come':   ['comes','came','coming'],
    'see':    ['sees','saw','seen','seeing'],
    'know':   ['knows','knew','known','knowing'],
    'think':  ['thinks','thought','thinking'],
    'feel':   ['feels','felt','feeling'],
    'say':    ['says','said','saying'],
    'tell':   ['tells','told','telling'],
    'make':   ['makes','made','making'],
    'get':    ['gets','got','gotten','getting'],
    'take':   ['takes','took','taken','taking'],
    'give':   ['gives','gave','given','giving'],
    'find':   ['finds','found','finding'],
    'put':    ['puts','putting'],
    'set':    ['sets','setting'],
    'keep':   ['keeps','kept','keeping'],
    'let':    ['lets','letting'],
    'turn':   ['turns','turned','turning'],
    'bring':  ['brings','brought','bringing'],
    'call':   ['calls','called','calling'],
    'try':    ['tries','tried','trying'],
    'start':  ['starts','started','starting'],
    'stop':   ['stops','stopped','stopping'],
    'follow': ['follows','followed','following'],
    'work':   ['works','worked','working'],
    'live':   ['lives','lived','living'],
    'mean':   ['means','meant','meaning'],
    'change': ['changes','changed','changing'],
    'show':   ['shows','showed','shown','showing'],
    'play':   ['plays','played','playing'],
    'run':    ['runs','ran','running'],
    'move':   ['moves','moved','moving'],
    'hold':   ['holds','held','holding'],
    'happen': ['happens','happened','happening'],
    'pay':    ['pays','paid','paying'],
    'fall':   ['falls','fell','fallen','falling'],
    'break':  ['breaks','broke','broken','breaking'],
    'cut':    ['cuts','cutting'],
    'lose':   ['loses','lost','losing'],
    'ask':    ['asks','asked','asking'],
    'need':   ['needs','needed','needing'],
    'leave':  ['leaves','left','leaving'],
    'learn':  ['learns','learned','learnt','learning'],
    'read':   ['reads','reading'],
    'look':   ['looks','looked','looking'],
    'stand':  ['stands','stood','standing'],
    'wait':   ['waits','waited','waiting'],
    'write':  ['writes','wrote','written','writing'],
    'become': ['becomes','became','becoming'],
    'spend':  ['spends','spent','spending'],
    'grow':   ['grows','grew','grown','growing'],
    'open':   ['opens','opened','opening'],
    'walk':   ['walks','walked','walking'],
    'win':    ['wins','won','winning'],
    'buy':    ['buys','bought','buying'],
    'send':   ['sends','sent','sending'],
    'build':  ['builds','built','building'],
    'die':    ['dies','died','dying'],
    'raise':  ['raises','raised','raising'],
    'pass':   ['passes','passed','passing'],
    'carry':  ['carries','carried','carrying'],
    'deal':   ['deals','dealt','dealing'],
    'drive':  ['drives','drove','driven','driving'],
    'hear':   ['hears','heard','hearing'],
    'sit':    ['sits','sat','sitting'],
    'meet':   ['meets','met','meeting'],
    'eat':    ['eats','ate','eaten','eating'],
    'lead':   ['leads','led','leading'],
    'speak':  ['speaks','spoke','spoken','speaking'],
    'wake':   ['wakes','woke','woken','waking'],
    'wear':   ['wears','wore','worn','wearing'],
    'wish':   ['wishes','wished','wishing'],
    'worry':  ['worries','worried','worrying'],
    'understand': ['understands','understood','understanding'],
    'choose': ['chooses','chose','chosen','choosing'],
    'reach':  ['reaches','reached','reaching'],
    'add':    ['adds','added','adding'],
    'act':    ['acts','acted','acting'],
    'watch':  ['watches','watched','watching'],
    'suggest':['suggests','suggested','suggesting'],
    'include':['includes','included','including'],
    'forget': ['forgets','forgot','forgotten','forgetting'],
    'allow':  ['allows','allowed','allowing'],
    'help':   ['helps','helped','helping'],
    'expect': ['expects','expected','expecting'],
    'like':   ['likes','liked','liking'],
    'want':   ['wants','wanted','wanting'],
    'aim':    ['aims','aimed','aiming'],
    'avoid':  ['avoids','avoided','avoiding'],
    'appear': ['appears','appeared','appearing'],
    'bear':   ['bears','bore','borne','bearing'],
    'begin':  ['begins','began','begun','beginning'],
    'bend':   ['bends','bent','bending'],
    'blow':   ['blows','blew','blown','blowing'],
    'burn':   ['burns','burned','burnt','burning'],
    'care':   ['cares','cared','caring'],
    'catch':  ['catches','caught','catching'],
    'claim':  ['claims','claimed','claiming'],
    'climb':  ['climbs','climbed','climbing'],
    'count':  ['counts','counted','counting'],
    'cover':  ['covers','covered','covering'],
    'cross':  ['crosses','crossed','crossing'],
    'dare':   ['dares','dared','daring'],
    'depend': ['depends','depended','depending'],
    'dive':   ['dives','dived','dove','diving'],
    'doubt':  ['doubts','doubted','doubting'],
    'drag':   ['drags','dragged','dragging'],
    'draw':   ['draws','drew','drawn','drawing'],
    'drop':   ['drops','dropped','dropping'],
    'end':    ['ends','ended','ending'],
    'fade':   ['fades','faded','fading'],
    'fail':   ['fails','failed','failing'],
    'fill':   ['fills','filled','filling'],
    'finish': ['finishes','finished','finishing'],
    'fit':    ['fits','fitted','fitting'],
    'fix':    ['fixes','fixed','fixing'],
    'focus':  ['focuses','focused','focusing'],
    'fold':   ['folds','folded','folding'],
    'gain':   ['gains','gained','gaining'],
    'grab':   ['grabs','grabbed','grabbing'],
    'grant':  ['grants','granted','granting'],
    'grip':   ['grips','gripped','gripping'],
    'guess':  ['guesses','guessed','guessing'],
    'hang':   ['hangs','hung','hanging'],
    'hope':   ['hopes','hoped','hoping'],
    'hurry':  ['hurries','hurried','hurrying'],
    'join':   ['joins','joined','joining'],
    'jump':   ['jumps','jumped','jumping'],
    'kick':   ['kicks','kicked','kicking'],
    'knock':  ['knocks','knocked','knocking'],
    'launch': ['launches','launched','launching'],
    'lay':    ['lays','laid','laying'],
    'lean':   ['leans','leaned','leant','leaning'],
    'lie':    ['lies','lay','lain','lying'],
    'lift':   ['lifts','lifted','lifting'],
    'link':   ['links','linked','linking'],
    'lock':   ['locks','locked','locking'],
    'love':   ['loves','loved','loving'],
    'miss':   ['misses','missed','missing'],
    'name':   ['names','named','naming'],
    'notice': ['notices','noticed','noticing'],
    'offer':  ['offers','offered','offering'],
    'owe':    ['owes','owed','owing'],
    'own':    ['owns','owned','owning'],
    'pick':   ['picks','picked','picking'],
    'plan':   ['plans','planned','planning'],
    'please': ['pleases','pleased','pleasing'],
    'pour':   ['pours','poured','pouring'],
    'press':  ['presses','pressed','pressing'],
    'prove':  ['proves','proved','proven','proving'],
    'pull':   ['pulls','pulled','pulling'],
    'push':   ['pushes','pushed','pushing'],
    'race':   ['races','raced','racing'],
    'realize':['realizes','realized','realizing','realises','realised','realising'],
    'refer':  ['refers','referred','referring'],
    'rely':   ['relies','relied','relying'],
    'remain': ['remains','remained','remaining'],
    'rescue': ['rescues','rescued','rescuing'],
    'reveal': ['reveals','revealed','revealing'],
    'ring':   ['rings','rang','rung','ringing'],
    'rise':   ['rises','rose','risen','rising'],
    'roll':   ['rolls','rolled','rolling'],
    'rush':   ['rushes','rushed','rushing'],
    'scratch':['scratches','scratched','scratching'],
    'seek':   ['seeks','sought','seeking'],
    'seem':   ['seems','seemed','seeming'],
    'sell':   ['sells','sold','selling'],
    'settle': ['settles','settled','settling'],
    'shake':  ['shakes','shook','shaken','shaking'],
    'share':  ['shares','shared','sharing'],
    'shed':   ['sheds','shedding'],
    'shut':   ['shuts','shutting'],
    'slide':  ['slides','slid','sliding'],
    'slip':   ['slips','slipped','slipping'],
    'snap':   ['snaps','snapped','snapping'],
    'spread': ['spreads','spreading'],
    'spring': ['springs','sprang','sprung','springing'],
    'stay':   ['stays','stayed','staying'],
    'step':   ['steps','stepped','stepping'],
    'stick':  ['sticks','stuck','sticking'],
    'stretch':['stretches','stretched','stretching'],
    'strike': ['strikes','struck','striking'],
    'stumble':['stumbles','stumbled','stumbling'],
    'sweep':  ['sweeps','swept','sweeping'],
    'switch': ['switches','switched','switching'],
    'talk':   ['talks','talked','talking'],
    'taste':  ['tastes','tasted','tasting'],
    'throw':  ['throws','threw','thrown','throwing'],
    'tie':    ['ties','tied','tying'],
    'touch':  ['touches','touched','touching'],
    'train':  ['trains','trained','training'],
    'treat':  ['treats','treated','treating'],
    'trust':  ['trusts','trusted','trusting'],
    'twist':  ['twists','twisted','twisting'],
    'value':  ['values','valued','valuing'],
    'visit':  ['visits','visited','visiting'],
    'wander': ['wanders','wandered','wandering'],
    'wave':   ['waves','waved','waving'],
    'wipe':   ['wipes','wiped','wiping'],
}

INFLECTION_TO_BASE = {}
_EXTRA_INFLECTIONS = {
    'be':     ['is','are','was','were','been','being','am'],
    'do':     ['does','did','done','doing'],
    'have':   ['has','had','having'],
    'go':     ['goes','went','gone','going'],
    'come':   ['comes','came','coming'],
    'see':    ['sees','saw','seen','seeing'],
    'know':   ['knows','knew','known','knowing'],
    'think':  ['thinks','thought','thinking'],
    'feel':   ['feels','felt','feeling'],
    'say':    ['says','said','saying'],
    'tell':   ['tells','told','telling'],
    'make':   ['makes','made','making'],
    'get':    ['gets','got','gotten','getting'],
    'take':   ['takes','took','taken','taking'],
    'give':   ['gives','gave','given','giving'],
    'find':   ['finds','found','finding'],
    'put':    ['puts','putting'],
    'set':    ['sets','setting'],
    'keep':   ['keeps','kept','keeping'],
    'let':    ['lets','letting'],
    'turn':   ['turns','turned','turning'],
    'bring':  ['brings','brought','bringing'],
    'call':   ['calls','called','calling'],
    'try':    ['tries','tried','trying'],
    'start':  ['starts','started','starting'],
    'stop':   ['stops','stopped','stopping'],
    'follow': ['follows','followed','following'],
    'work':   ['works','worked','working'],
    'live':   ['lives','lived','living'],
    'mean':   ['means','meant','meaning'],
    'change': ['changes','changed','changing'],
    'show':   ['shows','showed','shown','showing'],
    'play':   ['plays','played','playing'],
    'run':    ['runs','ran','running'],
    'move':   ['moves','moved','moving'],
    'hold':   ['holds','held','holding'],
    'happen': ['happens','happened','happening'],
    'pay':    ['pays','paid','paying'],
    'fall':   ['falls','fell','fallen','falling'],
    'break':  ['breaks','broke','broken','breaking'],
    'cut':    ['cuts','cutting'],
    'lose':   ['loses','lost','losing'],
    'ask':    ['asks','asked','asking'],
    'need':   ['needs','needed','needing'],
    'leave':  ['leaves','left','leaving'],
    'learn':  ['learns','learned','learnt','learning'],
    'read':   ['reads','reading'],
    'look':   ['looks','looked','looking'],
    'stand':  ['stands','stood','standing'],
    'wait':   ['waits','waited','waiting'],
    'write':  ['writes','wrote','written','writing'],
    'become': ['becomes','became','becoming'],
    'spend':  ['spends','spent','spending'],
    'grow':   ['grows','grew','grown','growing'],
    'open':   ['opens','opened','opening'],
    'walk':   ['walks','walked','walking'],
    'win':    ['wins','won','winning'],
    'buy':    ['buys','bought','buying'],
    'send':   ['sends','sent','sending'],
    'build':  ['builds','built','building'],
    'die':    ['dies','died','dying'],
    'raise':  ['raises','raised','raising'],
    'pass':   ['passes','passed','passing'],
    'carry':  ['carries','carried','carrying'],
    'deal':   ['deals','dealt','dealing'],
    'drive':  ['drives','drove','driven','driving'],
    'hear':   ['hears','heard','hearing'],
    'sit':    ['sits','sat','sitting'],
    'meet':   ['meets','met','meeting'],
    'eat':    ['eats','ate','eaten','eating'],
    'lead':   ['leads','led','leading'],
    'speak':  ['speaks','spoke','spoken','speaking'],
    'wake':   ['wakes','woke','woken','waking'],
    'wear':   ['wears','wore','worn','wearing'],
    'wish':   ['wishes','wished','wishing'],
    'worry':  ['worries','worried','worrying'],
    'understand': ['understands','understood','understanding'],
    'choose': ['chooses','chose','chosen','choosing'],
    'reach':  ['reaches','reached','reaching'],
    'add':    ['adds','added','adding'],
    'act':    ['acts','acted','acting'],
    'watch':  ['watches','watched','watching'],
    'suggest':['suggests','suggested','suggesting'],
    'include':['includes','included','including'],
    'forget': ['forgets','forgot','forgotten','forgetting'],
    'allow':  ['allows','allowed','allowing'],
    'help':   ['helps','helped','helping'],
    'expect': ['expects','expected','expecting'],
    'like':   ['likes','liked','liking'],
    'want':   ['wants','wanted','wanting'],
    'aim':    ['aims','aimed','aiming'],
    'avoid':  ['avoids','avoided','avoiding'],
    'appear': ['appears','appeared','appearing'],
    'bear':   ['bears','bore','borne','bearing'],
    'begin':  ['begins','began','begun','beginning'],
    'bend':   ['bends','bent','bending'],
    'bind':   ['binds','bound','binding'],  # bound→bind（与 IRREG_VERB 配套）
    'blow':   ['blows','blew','blown','blowing'],
    'burn':   ['burns','burned','burnt','burning'],
    'care':   ['cares','cared','caring'],
    'catch':  ['catches','caught','catching'],
    'claim':  ['claims','claimed','claiming'],
    'climb':  ['climbs','climbed','climbing'],
    'count':  ['counts','counted','counting'],
    'cover':  ['covers','covered','covering'],
    'cross':  ['crosses','crossed','crossing'],
    'dare':   ['dares','dared','daring'],
    'depend': ['depends','depended','depending'],
    'dive':   ['dives','dived','dove','diving'],
    'doubt':  ['doubts','doubted','doubting'],
    'drag':   ['drags','dragged','dragging'],
    'draw':   ['draws','drew','drawn','drawing'],
    'drop':   ['drops','dropped','dropping'],
    'end':    ['ends','ended','ending'],
    'fade':   ['fades','faded','fading'],
    'fail':   ['fails','failed','failing'],
    'fill':   ['fills','filled','filling'],
    'finish': ['finishes','finished','finishing'],
    'fit':    ['fits','fitted','fitting'],
    'fix':    ['fixes','fixed','fixing'],
    'focus':  ['focuses','focused','focusing'],
    'fold':   ['folds','folded','folding'],
    'gain':   ['gains','gained','gaining'],
    'grab':   ['grabs','grabbed','grabbing'],
    'grant':  ['grants','granted','granting'],
    'grip':   ['grips','gripped','gripping'],
    'guess':  ['guesses','guessed','guessing'],
    'hang':   ['hangs','hung','hanging'],
    'hope':   ['hopes','hoped','hoping'],
    'hurry':  ['hurries','hurried','hurrying'],
    'join':   ['joins','joined','joining'],
    'jump':   ['jumps','jumped','jumping'],
    'kick':   ['kicks','kicked','kicking'],
    'knock':  ['knocks','knocked','knocking'],
    'launch': ['launches','launched','launching'],
    'lay':    ['lays','laid','laying'],
    'lean':   ['leans','leaned','leant','leaning'],
    'lie':    ['lies','lay','lain','lying'],
    'lift':   ['lifts','lifted','lifting'],
    'link':   ['links','linked','linking'],
    'lock':   ['locks','locked','locking'],
    'love':   ['loves','loved','loving'],
    'miss':   ['misses','missed','missing'],
    'name':   ['names','named','naming'],
    'notice': ['notices','noticed','noticing'],
    'offer':  ['offers','offered','offering'],
    'owe':    ['owes','owed','owing'],
    'own':    ['owns','owned','owning'],
    'pick':   ['picks','picked','picking'],
    'plan':   ['plans','planned','planning'],
    'please': ['pleases','pleased','pleasing'],
    'pour':   ['pours','poured','pouring'],
    'press':  ['presses','pressed','pressing'],
    'prove':  ['proves','proved','proven','proving'],
    'pull':   ['pulls','pulled','pulling'],
    'push':   ['pushes','pushed','pushing'],
    'race':   ['races','raced','racing'],
    'realize':['realizes','realized','realizing','realises','realised','realising'],
    'refer':  ['refers','referred','referring'],
    'rely':   ['relies','relied','relying'],
    'remain': ['remains','remained','remaining'],
    'rescue': ['rescues','rescued','rescuing'],
    'reveal': ['reveals','revealed','revealing'],
    'ring':   ['rings','rang','rung','ringing'],
    'rise':   ['rises','rose','risen','rising'],
    'roll':   ['rolls','rolled','rolling'],
    'rush':   ['rushes','rushed','rushing'],
    'scratch':['scratches','scratched','scratching'],
    'seek':   ['seeks','sought','seeking'],
    'seem':   ['seems','seemed','seeming'],
    'sell':   ['sells','sold','selling'],
    'settle': ['settles','settled','settling'],
    'shake':  ['shakes','shook','shaken','shaking'],
    'share':  ['shares','shared','sharing'],
    'shed':   ['sheds','shedding'],
    'shut':   ['shuts','shutting'],
    'slide':  ['slides','slid','sliding'],
    'slip':   ['slips','slipped','slipping'],
    'snap':   ['snaps','snapped','snapping'],
    'spread': ['spreads','spreading'],
    'spring': ['springs','sprang','sprung','springing'],
    'stay':   ['stays','stayed','staying'],
    'step':   ['steps','stepped','stepping'],
    'stick':  ['sticks','stuck','sticking'],
    'stretch':['stretches','stretched','stretching'],
    'strike': ['strikes','struck','striking'],
    'stumble':['stumbles','stumbled','stumbling'],
    'sweep':  ['sweeps','swept','sweeping'],
    'switch': ['switches','switched','switching'],
    'talk':   ['talks','talked','talking'],
    'taste':  ['tastes','tasted','tasting'],
    'throw':  ['throws','threw','thrown','throwing'],
    'tie':    ['ties','tied','tying'],
    'touch':  ['touches','touched','touching'],
    'train':  ['trains','trained','training'],
    'treat':  ['treats','treated','treating'],
    'trust':  ['trusts','trusted','trusting'],
    'twist':  ['twists','twisted','twisting'],
    'value':  ['values','valued','valuing'],
    'visit':  ['visits','visited','visiting'],
    'wander': ['wanders','wandered','wandering'],
    'wave':   ['waves','waved','waving'],
    'wipe':   ['wipes','wiped','wiping'],
}

for _base, _forms in _EXTRA_INFLECTIONS.items():
    for _f in _forms:
        INFLECTION_TO_BASE[_f] = _base


# ─────────────────────────────────────────────────────────────────
# § 3  缩写展开表 CONTRACTIONS
# 完整版（57 条 + Unicode 撇号兜底），供 retester/matcher 的预处理层使用。
# generator 的 _expand_contractions 也从此导入（多余条目不匹配 EVP 短语，不影响生成）
# （多余条目不会匹配 EVP 短语，不影响生成结果）。
# ─────────────────────────────────────────────────────────────────

_CONTRACTIONS = {
    "ain't":    "am not",
    "aren't":   "are not",
    "can't":    "cannot",
    "couldn't": "could not",
    "didn't":   "did not",
    "doesn't":  "does not",
    "don't":    "do not",
    "hadn't":   "had not",
    "hasn't":   "has not",
    "haven't":  "have not",
    "he'd":     "he would",
    "he'll":    "he will",
    "he's":     "he is",
    "i'd":      "i would",
    "i'll":     "i will",
    "i'm":      "i am",
    "i've":     "i have",
    "isn't":    "is not",
    "it'd":     "it would",
    "it'll":    "it will",
    "it's":     "it is",
    "let's":    "let us",
    "mustn't":  "must not",
    "needn't":  "need not",
    "shan't":   "shall not",
    "she'd":    "she would",
    "she'll":   "she will",
    "she's":    "she is",
    "shouldn't":"should not",
    "that's":   "that is",
    "there's":  "there is",
    "they'd":   "they would",
    "they'll":  "they will",
    "they're":  "they are",
    "they've":  "they have",
    "wasn't":   "was not",
    "we'd":     "we would",
    "we'll":    "we will",
    "we're":    "we are",
    "we've":    "we have",
    "weren't":  "were not",
    "what'll":  "what will",
    "what're":  "what are",
    "what's":   "what is",
    "what've":  "what have",
    "where's":  "where is",
    "who'd":    "who would",
    "who'll":   "who will",
    "who're":   "who are",
    "who's":    "who is",
    "who've":   "who have",
    "won't":    "will not",
    "wouldn't": "would not",
    "you'd":    "you would",
    "you'll":   "you will",
    "you're":   "you are",
    "you've":   "you have",
    # Unicode 撇号变体
    "\u2019t":  " not",   # 兜底：'t → not（上面未覆盖时）
}


# ─────────────────────────────────────────────────────────────────
# § 4  不规则动词表 IRREG_VERB
# 过去式/过去分词 → 原形，供 retester/matcher 预处理层词形还原兜底使用。
# （WordNetLemmatizer 无法处理 fell→fall、broke→break 等不规则形式）
# 不规则动词形超集；新增条目在此添加即可。
# ─────────────────────────────────────────────────────────────────

_IRREG_VERB = {
    # be
    'was': 'be', 'were': 'be', 'been': 'be',
    # 高频不规则
    'fell': 'fall', 'fallen': 'fall',
    'broke': 'break', 'broken': 'break',
    'went': 'go', 'gone': 'go',
    'came': 'come',
    'took': 'take', 'taken': 'take',
    'got': 'get', 'gotten': 'get',
    'saw': 'see', 'seen': 'see',
    'held': 'hold',
    'bought': 'buy',
    'ran': 'run',
    'said': 'say',
    'told': 'tell',
    'lost': 'lose',
    'found': 'find',
    'left': 'leave',
    'stood': 'stand',
    'kept': 'keep',
    'meant': 'mean',
    'chose': 'choose', 'chosen': 'choose',
    'wore': 'wear', 'worn': 'wear',
    'began': 'begin', 'begun': 'begin',
    'built': 'build',
    'drew': 'draw', 'drawn': 'draw',
    'drove': 'drive', 'driven': 'drive',
    'felt': 'feel',
    'grew': 'grow', 'grown': 'grow',
    'knew': 'know', 'known': 'know',
    'led': 'lead',
    'lay': 'lie',
    'met': 'meet',
    'paid': 'pay',
    'rose': 'rise', 'risen': 'rise',
    'sent': 'send',
    'spoke': 'speak', 'spoken': 'speak',
    'stuck': 'stick',
    'threw': 'throw', 'thrown': 'throw',
    'won': 'win',
    'wrote': 'write', 'written': 'write',
    'brought': 'bring',
    'caught': 'catch',
    'fought': 'fight',
    'forgave': 'forgive', 'forgiven': 'forgive',
    'gave': 'give', 'given': 'give',
    'heard': 'hear',
    'hid': 'hide', 'hidden': 'hide',
    'hit': 'hit',
    'hung': 'hang',
    'lent': 'lend',
    'lit': 'light',
    'lost': 'lose',
    'made': 'make',
    'put': 'put',
    'quit': 'quit',
    'read': 'read',
    'rode': 'ride', 'ridden': 'ride',
    'sang': 'sing', 'sung': 'sing',
    'sank': 'sink', 'sunk': 'sink',
    'sat': 'sit',
    'slept': 'sleep',
    'sold': 'sell',
    'set': 'set',
    'shot': 'shoot',
    'showed': 'show', 'shown': 'show',
    'shut': 'shut',
    'spent': 'spend',
    'split': 'split',
    'spread': 'spread',
    'stole': 'steal', 'stolen': 'steal',
    'swept': 'sweep',
    'swam': 'swim', 'swum': 'swim',
    'swung': 'swing',
    'taught': 'teach',
    'tore': 'tear', 'torn': 'tear',
    'thought': 'think',
    'understood': 'understand',
    'woke': 'wake', 'woken': 'wake',
    'bound': 'bind',   # "be bound to" 归一化后 bound→bind
}


# ─────────────────────────────────────────────────────────────────
# § 5  代词归一集合
# ─────────────────────────────────────────────────────────────────

# 物主代词 → your（PRP$ 标签时归一）
_POSS_TO_YOUR = {
    'my', 'his', 'their', 'our', "one's",
}

# 反身代词 → yourself
_REFL_TO_YOURSELF = {
    'myself', 'himself', 'herself', 'themselves', 'ourselves', 'oneself',
}

# 人称代词 → _sb_（宾格 + 主格，排除 you/it）
_PRONOUN_TO_SB = {
    'he', 'she', 'him', 'her', 'they', 'them',
    'me', 'us', 'we',
    'someone', 'somebody', 'everyone', 'everybody',
    'anyone', 'anybody', 'nobody', 'no one',
}


# ─────────────────────────────────────────────────────────────────
# § 6  正则常量
# 供 generator phrase_to_regex 使用。如需调整数字匹配范围、时间单位
# 集合、冠词列表等，在此修改，generator 自动生效。
# ─────────────────────────────────────────────────────────────────

_TIMEUNIT_RE = (
    r'(?:days?|weeks?|months?|years?|hours?|minutes?|seconds?'
    r'|decades?|centur(?:y|ies)|mornings?|afternoons?|evenings?|nights?'
    r'|seasons?|terms?|quarters?|fortnights?|moments?|instants?'
    r'|semesters?|periods?|ages?|eras?|generations?)'
)

_NUM_RE = (
    r'(?:'
    # ── 合成十位数（twenty-one … ninety-nine）——需在 tens 和 ones 之前 ──
    r'(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)'
    r'(?:-(?:one|two|three|four|five|six|seven|eight|nine))?'
    r'|'
    # ── 11-19（teens）——需在 ones 之前避免 "nine" 先命中 "nineteen" ──
    r'(?:eleven|twelve|thirteen|fourteen|fifteen|sixteen'
    r'|seventeen|eighteen|nineteen)'
    r'|'
    # ── 1-10 基础数词 ──
    r'(?:one|two|three|four|five|six|seven|eight|nine|ten)'
    r'|'
    # ── 大数词（hundred/thousand/million/billion，可带前置 a） ──
    r'(?:a\s+)?(?:hundred|thousand|million|billion)'
    r'|'
    # ── 分数词 ──
    r'(?:half|quarter)'
    r'|'
    # ── 阿拉伯数字（含小数 6.30、年代后缀 1870s、百分比 65% 等） ──
    r'\d+(?:[.,]\d+)*[a-z%]*'
    r')'
)

# 宽松限定词组（Step 9b 冠词泛化，覆盖 a/an 位置的常见替换词）
_DET = r'(?:a|an|the|this|that|no|every|each|one|two|three|several|any|your|my)'

# PH_SBPOS 展开式（覆盖三种归一化形态）
#   "your disposal"             ← 简单物主代词归一（无 's）
#   "your father 's footsteps"  ← 物主 + 名词 + 's token
#   "the company 's disposal"   ← 定冠词 + 名词 + 's token
#   "your interests"            ← your + 复数名词（无 's）
_SBPOS_RE = r"(?:your(?:\s+\w+(?:\s+'s)?)?|the(?:\s+\w+)?\s+'s)"

# ─────────────────────────────────────────────────────────────────
# § 7  词形还原/匹配用词表
# 供 generator 的短语动词词形还原与占位符展开使用。均为纯词表，
# 在此增删，generator 自动生效。
# ─────────────────────────────────────────────────────────────────

# 这些 -ing 词在 EVP 短语里是形容词用法（JJ），matcher 在句子语境中也标为
# JJ 而不还原；生成器不还原以保持正则与归一化文本一致。
_JJ_ING_ADJECTIVES = frozenset({
    'laughing',    # no laughing matter
    'running',     # running water
    'following',   # the following
    'existing',    # existing rules/conditions
    'remaining',   # remaining time
    'interesting', 'boring', 'relaxing', 'exciting',
})

# -ed 词在 EVP 短语里是形容词用法（be/get + adj 结构），不应还原。
# 生成器据此生成 (?:ed_form|base_form) 备选正则，兼容两种归一化结果。
_JJ_ED_ADJECTIVES = frozenset({
    'accustomed',   # be accustomed to
    'absorbed',     # be absorbed in
    'aimed',        # be aimed at
    'armed',        # be armed with
    'ashamed',      # be ashamed of
    'associated',   # be associated with
    'balanced',     # a balanced diet
    'based',        # be based on
    'compared',     # compared to/with
    'concentrated', # be concentrated in
    'confronted',   # be confronted with
    'connected',    # be connected to
    'consumed',     # be consumed by
    'considered',   # be considered
    'dedicated',    # be dedicated to
    'descended',    # be descended from
    'designed',     # be designed for
    'divorced',     # be divorced from
    'educated',     # be educated at
    'experienced',  # experienced in
    'hooked',       # be hooked on
    'inclined',     # be inclined to
    'involved',     # be involved in
    'interested',   # be interested in
    'limited',      # be limited to
    'located',      # be located in
    'mixed',        # mixed feelings
    'obsessed',     # be obsessed with
    'opposed',      # be opposed to
    'peeled',       # keep your eyes peeled
    'pleased',      # be pleased with
    'pointed',      # pointed out
    'related',      # be related to
    'reserved',     # be reserved for
    'situated',     # be situated in
    'snowed',       # be snowed under
    'suited',       # be suited to
    'supposed',     # be supposed to
    'tired',        # be tired of
    'twisted',      # twisted logic
    'unexpected',   # unexpected event
    'worried',      # be worried about
})

# 短语动词词形还原时跳过的功能词（不作动词还原处理）。
_PHRASE_VERB_SKIP = frozenset({
    'sb', 'sth', 'swh',
    'do', 'doing', 'be', 'have',
    'not', 'no', 'nor',
    'the', 'a', 'an',
    'to', 'of', 'in', 'on', 'at', 'for', 'with', 'by',
    'from', 'into', 'out', 'up', 'down', 'off', 'over',
    'about', 'after', 'before', 'through', 'between', 'among',
    'your', 'yourself', 'any', 'some', 'all', 'one', 'each', 'every',
})

# 年代词（be in your twenties / the eighties 等的合并规则用）
_DECADE_RE = (
    r'(?:teens|twenties|thirties|forties|fifties|sixties'
    r'|seventies|eighties|nineties)'
)

# do/doing sth 位置的负向前瞻：排除功能词（冠词、介词、代词、情态动词、
# 常见连词/副词），防止 "avoid the problem" / "avoid in time" 之类误命中。
# 用负向前瞻排除功能词后接 \w+，而非枚举动词词表。
_VERB_NEG_LA = (
    r'(?!'
    r'(?:the|a|an|this|that|these|those|every|each|any|some|no|my|your)\b'
    r'|'
    r'(?:in|on|at|of|for|with|by|from|into|out|up|down|off|over|about'
    r'|after|before|through|between|among|against|during|without)\b'
    r'|'
    r'(?:i|you|he|she|it|we|they|_sb_|who|what|which|how|why|when|where)\b'
    r'|'
    r'(?:will|would|can|could|shall|should|may|might|must|need|dare)\b'
    r'|'
    r'(?:not|never|always|also|just|only|very|too|so|yet|still|even|now)\b'
    r')'
)

# sb 占位符首词排除集：sb 是"人"，其首词不应是
#   (a) 高频动词原形（阻止 "without/leave sb" 误匹配 prep+动名词，having→have）；
#   (b) 高频【非人称】名词/地点（阻止 "get to sb"→"get to your house"、
#       "hear from sb"→"hear from your garden" 等误配）。
# 预处理器把动名词还原为原形，故动词列原形。
# 名词列仅含【明确无生命】词，绝不含可指人的词(friend/teacher/doctor…)，
# 以免误排真正的 sb；两处前瞻共用同一份名词集(_SB_NON_PERSON)保持一致。
_SB_NOT_PERSON_VERBS = (
    r'be|have|do|get|go|make|take|give|come|keep|put|use|work|try|help|'
    r'look|find|see|know|think|talk|walk|play|run|read|write|eat|sit|stand|'
    r'leave|bring|hold|feel|say|tell|ask|turn|start|stop|move|live|bear|'
    r'wait|warn|meet|hear|watch|begin|happen'
)
_SB_NON_PERSON = (
    r'house|home|place|part|room|key|door|car|way|thing|time|work|school|world|'
    r'area|side|city|country|office|shop|street|building|money|life|programme|'
    r'program|show|shopping|'
    r'garden|book|letter|phone|computer|video|trip|concert|camp|weather|'
    r'suggestion|plan|interview|word|river|cash|entrance|clothes|future|stage|'
    r'call|bank|food|music|film|game|party|holiday|weekend|station|hospital|'
    r'hotel|restaurant|kitchen|ticket|price|problem|question|idea|story|news|'
    r'gift|photo|picture|song|sea|beach|park|town|bag|present|website|email'
)
_SB_NOT_VERB_LA = (
    r'(?!(?:' + _SB_NOT_PERSON_VERBS + r'|' + _SB_NON_PERSON + r')\b)'
    r'(?!(?:your|my|the|a|an|this|that|his|her|its|our)\s+(?:'
    + _SB_NON_PERSON + r')\b)'
)

# ─────────────────────────────────────────────────────────────────
# 公开别名（供导入时使用无下划线前缀的名称）
# ─────────────────────────────────────────────────────────────────
CONTRACTIONS = _CONTRACTIONS
IRREG_VERB   = _IRREG_VERB
POSS_TO_YOUR      = _POSS_TO_YOUR
REFL_TO_YOURSELF  = _REFL_TO_YOURSELF
PRONOUN_TO_SB     = _PRONOUN_TO_SB
TIMEUNIT_RE  = _TIMEUNIT_RE
NUM_RE       = _NUM_RE
DET          = _DET
SBPOS_RE     = _SBPOS_RE
JJ_ING_ADJECTIVES = _JJ_ING_ADJECTIVES
JJ_ED_ADJECTIVES  = _JJ_ED_ADJECTIVES
PHRASE_VERB_SKIP  = _PHRASE_VERB_SKIP
DECADE_RE    = _DECADE_RE
VERB_NEG_LA  = _VERB_NEG_LA
SB_NOT_VERB_LA = _SB_NOT_VERB_LA
