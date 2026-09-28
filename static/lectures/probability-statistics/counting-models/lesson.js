/* Authored slide states. Colors always have accompanying words or symbols.
   Params: stage controls successive reveals; n,p,k describe binomial counts;
   N,K,n,k describe finite sampling; focus identifies the equation/picture part;
   sample is a 0/1 pictured outcome; highlighted indices are zero-based.
   mode is a conceptual label; trials is the requested simulation count;
   lambda is expected count in the selected window; rate, area, seconds retain units.
   Semantic ids are stable links; anchors are labels in the companion LaTeX source. */
(() => {
  const R = String.raw;
  const details = [];
  const add = (id, section, title, body, eq, visual, params, notes, anchor) => {
    // Renderer-facing aliases keep the pedagogical meanings explicit.
    if (visual === 'sequence') {
      params.pattern = params.sample || Array.from({length:params.n}, (_,i) => i < (params.k ?? Math.round(params.n*params.p)) ? 1 : 0);
      params.revealCount ??= params.n;
      params.concealed ??= id === 'marginal-shuffle' || id === 'marginal-position';
      params.dependent ??= /^(hypergeometric|marginal|variance)-/.test(id);
    }
    if (visual === 'pascal') {
      params.row = params.n;
      params.highlightRow = params.n;
      params.highlightCol = params.k;
    }
    if (visual === 'cereal') params.region = params.mode === 'miss' ? 'miss' : params.mode === 'none' ? 'none' : 'reject';
    if (visual === 'hypergeom') {
      params.selectedSuccess = params.stage >= 1 ? params.k : 0;
      params.selectedFailure = params.stage >= 2 ? params.n-params.k : 0;
      params.replacement = false;
    }
    if (visual === 'urn') {
      params.replacement = params.mode === 'replacement';
      params.selectedSuccess = params.focus === 'remove-success' || params.focus === 'joint' || params.focus === 'return' ? 1 : params.focus === 'all' ? params.K : params.focus === 'sample' ? params.k : 0;
      params.selectedFailure = params.focus === 'remove-failure' ? 1 : params.focus === 'all' ? params.N-params.K : params.focus === 'sample' ? params.n-params.k : 0;
    }
    if (visual === 'rain') params.count = params.k ?? Math.round(params.lambda);
    if (visual === 'hyperlimit' || visual === 'poissonlimit') params.showSimulation = params.focus === 'simulation';
    details.push({id,section,title,body,eq,visual,params,notes,anchor});
  };
  const B = 'One trial → a count';
  const coin = {experiment:'coin',p:.5,successLabel:'heads',failureLabel:'tails',successSymbol:'H',failureSymbol:'T'};
  const die = {experiment:'die',p:1/3,successOutcomes:[5,6],successLabel:'5 or 6',failureLabel:'1, 2, 3, or 4',successSymbol:'S',failureSymbol:'F'};
  add('bernoulli-trial',B,'Start with a fair coin','One flip produces one outcome.', '', 'bernoulli',{...coin,stage:-1,focus:'trial'},'Begin with a familiar object, before formulas. A trial is one performance of the experiment. Decide before flipping that heads is the event to count.','bernoulli-start');
  add('bernoulli-labels',B,'Choose which outcome to count','Call heads success and tails failure.','','bernoulli',{...coin,stage:0,focus:'outcomes'},'Success and failure are neutral labels. They need not mean good and bad. The outcome labels here come from the coin, not from a candy color.','bernoulli-start');
  add('bernoulli-outcomes',B,'Give heads a probability','For this fair coin, p = 1/2.',R`\textcolor{#eab308}{P(\text{heads})=p=\frac12}`,'bernoulli',{...coin,stage:1,focus:'probabilities'},'The probability p belongs to the event selected as success. The same notation will work later for trials with different success probabilities.','bernoulli-start');
  add('bernoulli-failure-chance',B,'Tails gets the remaining probability','The two mutually exclusive possibilities cover every flip.',R`\textcolor{#eab308}{p=P(\text{heads})=\frac12}\qquad\textcolor{#38bdf8}{q=P(\text{tails})=1-p=\frac12}`, 'bernoulli',{...coin,stage:1,focus:'failure-probability'},'Because heads and tails exhaust the possibilities, their probabilities sum to one. For this fair coin both probabilities are one half.','bernoulli-start');
  add('bernoulli-variable',B,'Turn the outcome into a zero-or-one record','Heads contributes one; tails contributes zero.',R`I=\begin{cases}\textcolor{#eab308}{1},&\text{heads},\\\textcolor{#38bdf8}{0},&\text{tails}.\end{cases}`,'bernoulli',{...coin,stage:2,focus:'values'},'The random variable is the numerical record, not the coin itself. It records whether our chosen event occurred.','bernoulli-start');
  add('bernoulli-name',B,'This record is a Bernoulli variable','An indicator is simply this zero-or-one Bernoulli record.',R`I\sim\operatorname{Bernoulli}(p),\qquad p=\frac12`,'bernoulli',{...coin,stage:2,focus:'values'},'Whenever we say indicator, remember the Bernoulli variable that is one when an event occurs and zero otherwise.','bernoulli-start');
  add('bernoulli-die-outcomes',B,'The experiment can have more than two outcomes','A fair die has six equally likely faces.','','bernoulli',{...die,stage:-1,focus:'trial'},'The raw die outcome takes six possible values. It is not a Bernoulli variable. We next choose an event and record only whether it happened.','bernoulli-start');
  add('bernoulli-die-success',B,'Choose an event: roll a five or a six','Group {5, 6} as success; all other faces are failure.','','bernoulli',{...die,stage:0,focus:'outcomes'},'Success can be any chosen subset of the original outcomes. The two groups must cover every outcome and must not overlap.','bernoulli-start');
  add('bernoulli-die-probability',B,'Count the faces in each group','Two of the six equally likely faces belong to success.',R`p=\frac26=\frac13,\qquad q=\frac46=\frac23`,'bernoulli',{...die,stage:1,focus:'probabilities'},'A fair die need not produce a Bernoulli variable with probability one half: that depends on the event we chose. Here the success event has two faces.','bernoulli-start');
  add('bernoulli-die-variable',B,'Record the group, not the face number','The die outcome has six values; this record has only two.',R`I=\begin{cases}\textcolor{#eab308}{1},&\text{roll }5\text{ or }6,\\\textcolor{#38bdf8}{0},&\text{roll }1,2,3,\text{ or }4.\end{cases}`,'bernoulli',{...die,stage:2,focus:'values'},'Rolling a six makes the Bernoulli record one, not six. The coin record and this die-event record have the same zero-or-one structure, with different p.','bernoulli-start');
  add('bernoulli-mean',B,'Average the two possible recorded values','Multiply each value by its probability, then add.',R`E[I]=\textcolor{#eab308}{1\cdot p}+\textcolor{#38bdf8}{0\cdot q}=p`,'bernoulli',{...die,stage:3,focus:'mean'},'The mean is a long-run average, not another possible value. For the die event the expected Bernoulli record is one third, although each observed record is zero or one.','bernoulli-start');
  add('bernoulli-square',B,'Squaring changes neither recorded value','Zero squared is zero; one squared is one.',R`I^2=I\quad\Longrightarrow\quad E[I^2]=E[I]=p`,'bernoulli',{...die,stage:4,focus:'square'},'This identity is true for every outcome. It makes the variance calculation short.','bernoulli-start');
  add('bernoulli-variance',B,'Use the second-moment formula','Subtract the square of the mean.',R`\operatorname{Var}(I)=E[I^2]-(E[I])^2=p-p^2=\textcolor{#eab308}{p}\textcolor{#38bdf8}{q}`,'bernoulli',{...die,stage:5,focus:'variance'},'Remember that E[I squared] and the square of E[I] are different quantities. For a Bernoulli variable they are p and p squared.','bernoulli-start');
  add('bernoulli-deviations',B,'The definition gives the same variance','The deviations from the mean p are 1 − p and −p.',R`\operatorname{Var}(I)=p(1-p)^2+(1-p)p^2`,'bernoulli',{...die,stage:5,focus:'variance'},'Square each possible deviation from the mean and weight it by its probability. Success contributes p times (1-p) squared; failure contributes (1-p) times p squared.','bernoulli-start');
  add('bernoulli-deviations-factor',B,'Factor the two contributions','The remaining bracket totals one.',R`\operatorname{Var}(I)=p(1-p)\bigl[(1-p)+p\bigr]=pq`,'bernoulli',{...die,stage:5,focus:'variance'},'This agrees with the second-moment derivation. They compute the same variance by two different routes.','bernoulli-start');
  add('bernoulli-most-variable',B,'A fair coin gives the largest Bernoulli variance','Return to the coin: p = 1/2 makes the outcomes most uncertain.',R`p(1-p)=\frac14-\left(p-\frac12\right)^2\le\frac14`,'bernoulli',{...coin,stage:5,focus:'variance'},'The squared term is nonnegative. Variance is largest at p one half, where it equals one quarter. This compares Bernoulli models with different success probabilities.','bernoulli-start');
  add('bernoulli-endpoints',B,'A coin that always lands heads has no variation','Now change the model to certainty: p = 1.',R`\operatorname{Var}(I)=p(1-p)=0\quad\text{when }p\in\{0,1\}`,'bernoulli',{...coin,stage:5,p:1,focus:'variance'},'This is a different coin model, used to check the formula. A variable that never changes has variance zero. The same is true if success is impossible.','bernoulli-start');
  add('count-five-trials',B,'Flip the fair coin five times','Heads records 1; tails records 0.','','sequence',{stage:0,...coin,n:5,k:2,sample:[1,0,0,1,0],revealCount:0,focus:'reveal'},'Return to independent flips of the fair coin. One animation reveals the five outcomes in sequence, keeping the positions fixed, then holds on the resulting count.','binomial-start');
  for(let count=1;count<=5;count++){
    add(`count-reveal-${count}`,B,'Flip the fair coin five times','Heads records 1; tails records 0.','','sequence',{stage:0,...coin,n:5,k:2,sample:[1,0,0,1,0],revealCount:count,focus:'reveal',highlight:[count-1]},'The animation reveals these outcomes automatically in one short sequence. Adding the zero-or-one Bernoulli records counts heads. No probability multiplication has been assumed yet.','binomial-start');
  }
  add('bernoulli-sum',B,'Now repeat the trial','Each pictured zero or one is a Bernoulli variable.',R`X=I_1+\cdots+I_{\textcolor{#eab308}{n}}`,'sequence',{stage:0,...coin,n:5,k:2,sample:[1,0,0,1,0],focus:'sum'},'On this pictured outcome, one plus zero plus zero plus one plus zero equals two. Adding the Bernoulli variables counts successes. This counting identity alone says nothing about independence.','binomial-moments');
  add('binomial-fixed-trials',B,'Fix the number of trials','Here the experiment always uses five flips.',R`n=5`,'sequence',{stage:0,...coin,n:5,k:2,sample:[1,0,0,1,0],focus:'count'},'A binomial experiment has a predetermined number of trials. Stopping when a success appears describes a different experiment.','binomial-start');
  add('binomial-common-chance',B,'Use the same success chance each time','Each Bernoulli trial has probability p.',R`P(I_i=1)=p`,'sequence',{stage:1,...coin,n:5,k:2,sample:[1,0,0,1,0],focus:'common-p'},'Equal success chances alone do not establish independence. Sampling without replacement will give an important counterexample.','binomial-start');
  add('binomial-independent-trials',B,'Earlier outcomes give no information about the next','This is the independence requirement.','','sequence',{stage:1,...coin,n:5,k:2,sample:[1,0,0,1,0],focus:'independence'},'In the binomial model the trials are mutually independent. Knowing earlier outcomes leaves the next success chance unchanged.','binomial-start');
  add('binomial-assumptions',B,'Add the binomial assumptions','Use a fixed number of independent trials, all with the same p.',R`X\sim\operatorname{Bin}(n,p)`,'sequence',{stage:1,...coin,n:5,k:2,sample:[1,0,0,1,0],focus:'independence'},'The count is binomial when the zero-or-one Bernoulli variables are independent and share the same success probability. Later, sampling without replacement will break independence.','binomial-start');

  const C = 'Count the arrangements';
  add('binomial-general-p',C,'Keep the counting idea; change the success chance','For the next example, each independent trial succeeds with p = 0.3.',R`p=0.3,\qquad q=0.7`,'sequence',{stage:1,n:5,p:.3,k:2,sample:[1,0,0,1,0],focus:'common-p'},'The previous fair-coin example had p equal to one half. Now use a generic success/failure trial with p equal to 0.3. S and F name the two event categories; they are not candy colors.','counting-start');
  add('sequence-success-factors',C,'First follow the success factors','This one sequence has two successes.',R`P(SFFSF)=\textcolor{#a855f7}{p}\,q\,q\,\textcolor{#a855f7}{p}\,q`,'sequence',{stage:2,n:5,p:.3,k:2,sample:[1,0,0,1,0],focus:'success'},'Point only to the success positions first. Each success contributes a factor of p. The factors multiply because these trials are independent.','counting-start');
  add('sequence-failure-factors',C,'Now follow the failure factors','The other three positions are failures.',R`P(SFFSF)=p\,\textcolor{#14b8a6}{q}\,\textcolor{#14b8a6}{q}\,p\,\textcolor{#14b8a6}{q}=\textcolor{#a855f7}{p^2}\textcolor{#14b8a6}{q^3}`,'sequence',{stage:3,n:5,p:.3,k:2,sample:[1,0,0,1,0],focus:'failure'},'Now point to the failure positions. There are three factors of q because five minus two equals three.','counting-start');
  add('sequence-rearrange',C,'Move a success to a new position','The arrangement changes; its probability stays p²q³.',R`P(SFFSF)=P(FSSFF)=p^2q^3`,'sequence',{stage:4,n:5,p:.3,k:2,sample:[0,1,1,0,0],focus:'rearrange'},'The multiplication order changes, but the same two p factors and three q factors remain. We have found different outcomes with the same count.','counting-start');
  add('count-event',C,'Find every two-success arrangement','Keep two successes; change their positions.',R`\text{each arrangement has probability }p^2q^3`,'combinations',{stage:0,n:5,k:2,p:.3,focus:'arrangements',showCount:1},'Each row is a distinct possible ordered sequence. A single experiment lands in just one row, so these events are disjoint.','counting-start');
  for(let row=2;row<=10;row++){
    add(`count-arrangement-${row}`,C,'Find every two-success arrangement','Keep two successes; change their positions.',R`\text{each arrangement has probability }p^2q^3`,'combinations',{stage:0,n:5,k:2,p:.3,focus:'arrangements',showCount:row,highlight:row-1},'Each row is a different ordered outcome with exactly two successes. The rows are disjoint possibilities, so their probabilities can be added.','counting-start');
  }
  add('count-ordered-choices',C,'Choose success positions one at a time','There are five choices for the first position, then four.',R`\text{ordered choices}=5\cdot4=20`,'combinations',{stage:1,n:5,k:2,p:.3,focus:'ordered'},'We temporarily label which chosen position was chosen first. Choosing positions one then four and four then one produces the same final success locations.','counting-start');
  add('count-remove-order',C,'Remove the duplicate ordering','Each pair of success positions was counted twice.',R`\binom52=\frac{5\cdot4}{2\cdot1}=10`,'combinations',{stage:2,n:5,k:2,p:.3,focus:'coefficient'},'The two successes are not distinguishable. Divide by two factorial to count each set of success positions once.','counting-start');
  add('count-general',C,'Generalize the position count','Choose k of the n trial positions for successes.',R`\textcolor{#eab308}{\binom nk=\frac{n!}{k!(n-k)!}}`,'combinations',{stage:3,n:5,k:2,p:.3,focus:'coefficient'},'There are n times n minus one through n minus k plus one ordered selections. Divide by k factorial because every set of k chosen positions has that many orderings.','counting-start');
  add('binomial-one-term',C,'Multiply count by probability per sequence','All these disjoint sequences have the same probability.',R`P(X=k)=\underbrace{\textcolor{#eab308}{\binom nk}}_{\text{arrangements}}\underbrace{\textcolor{#a855f7}{p^k}\textcolor{#14b8a6}{q^{n-k}}}_{\text{one arrangement}}`,'combinations',{stage:4,n:5,k:2,p:.3,focus:'product'},'The binomial coefficient counts the sequences. It is not itself a probability. The remaining factors give the probability of one sequence.','binomial-start');
  add('binomial-example',C,'Evaluate one bar','For five trials with p = 0.3, exactly two successes has probability 0.3087.',R`P(X=2)=\binom52(0.3)^2(0.7)^3=0.3087`,'binomial',{stage:0,n:5,k:2,p:.3,focus:'bar'},'A probability mass function assigns one probability to each possible integer count. This calculation supplies the height of the bar at two.','binomial-start');
  add('binomial-support',C,'Repeat for every possible count','A count from five trials can only be 0, 1, 2, 3, 4, or 5.',R`P(X=k)=\binom nk p^kq^{n-k},\qquad k=0,\ldots,n`,'binomial',{stage:1,n:5,p:.3,focus:'all'},'Outside these integer values the probability is zero. We next explain why the probabilities across all these bars total one.','binomial-start');

  const P = 'Pascal → binomial theorem';
  add('pascal-row-zero',P,'Begin with an empty set of positions','There is one way to choose nothing.',R`\binom00=1`,'pascal',{stage:0,n:0,k:0,focus:'row'},'Row zero is useful: zero trials have exactly one possible sequence, the empty sequence.','normalization-start');
  // Each row builds automatically within a short beat; its parents remain visible.
  const chooseSmall=(n,k)=>{if(k<0||k>n)return 0;let v=1;for(let j=1;j<=k;j++)v=v*(n-j+1)/j;return Math.round(v);};
  for(let row=1;row<=5;row++)for(let col=0;col<=row;col++){
    const edge=col===0||col===row,a=chooseSmall(row-1,col-1),b=chooseSmall(row-1,col),value=chooseSmall(row,col);
    add(`pascal-build-${row}-${col}`,P,`Build row ${row} from the row above`,'The edges are 1; each interior entry adds its two parents.',
      edge?R`\binom{${row}}{${col}}=1`:R`\binom{${row}}{${col}}=\binom{${row-1}}{${col-1}}+\binom{${row-1}}{${col}}=\textcolor{#a855f7}{${a}}+\textcolor{#a855f7}{${b}}=\textcolor{#eab308}{${value}}`,
      'pascal',{n:row,k:col,stage:row,revealCol:col,focus:edge?'edge':'sum'},
      edge?'There is exactly one empty subset and exactly one subset containing all positions.':'The parent entries count disjoint cases: include the new position or exclude it. Each row reveals its entries automatically, then pauses for inspection.','normalization-start');
  }
  add('pascal-edge',P,'Every row has a one at each edge','Choose no positions, or choose every position.',R`\binom n0=\binom nn=1`,'pascal',{stage:1,n:4,k:0,focus:'edges'},'The left edge means all failures. The right edge means all successes. Each is exactly one arrangement.','normalization-start');
  add('pascal-exclude',P,'A chosen set may exclude the last position','Then all k success positions come from the first n − 1.',R`\text{last position fails: }\binom{n-1}{k}`,'pascal',{stage:2,n:5,k:2,focus:'left-parent'},'To count sets of success positions, split them according to whether the last position is chosen. First hold only the excluded case.','normalization-start');
  add('pascal-include',P,'Or it may include the last position','Then choose k − 1 more success positions among the first n − 1.',R`\text{last position succeeds: }\binom{n-1}{k-1}`,'pascal',{stage:3,n:5,k:2,focus:'right-parent'},'The last success is already committed. Only k minus one success positions remain to choose.','normalization-start');
  add('pascal-add',P,'Add the two disjoint cases','The two entries above build the entry below.',R`\binom nk=\binom{n-1}{k}+\binom{n-1}{k-1}`,'pascal',{stage:4,n:5,k:2,focus:'sum'},'Every set includes the last position or excludes it, never both. This explains Pascal’s addition rule by counting, without factorial algebra.','normalization-start');
  add('pascal-five',P,'Read the completed fifth row','Each entry counts arrangements with that many successes.',R`\binom50,\binom51,\ldots,\binom55=1,5,10,10,5,1`,'pascal',{stage:5,n:5,k:2,focus:'row'},'Row five is now complete. The highlighted ten is the same ten arrangements of two successes among five trials; the animation built each entry from its two parents.','normalization-start');
  add('theorem-factors',P,'Read a product as choices','From each factor choose either p or q.',R`(p+q)^3=(p+q)(p+q)(p+q)`,'sequence',{stage:0,n:3,k:1,p:.5,sample:[1,0,0],focus:'factors'},'Expanding a product means choosing one term from each factor, then multiplying those chosen terms. Each sequence of choices matches one pictured success/failure sequence.','normalization-start');
  add('theorem-like-terms',P,'Collect choices with the same count','Three arrangements contribute pq².',R`\textcolor{#a855f7}{p}\textcolor{#14b8a6}{qq}+\textcolor{#14b8a6}{q}\textcolor{#a855f7}{p}\textcolor{#14b8a6}{q}+\textcolor{#14b8a6}{qq}\textcolor{#a855f7}{p}=\textcolor{#eab308}{3}pq^2`,'combinations',{stage:4,n:3,k:1,p:.5,focus:'product'},'The coefficient three has a concrete counting meaning: choose which one of the three factors supplied p.','normalization-start');
  add('binomial-theorem',P,'The coefficients are the same position counts','For k copies of p, choose which k factors supply them.',R`(p+q)^n=\sum_{k=0}^{n}\textcolor{#eab308}{\binom nk}\textcolor{#a855f7}{p^k}\textcolor{#14b8a6}{q^{n-k}}`,'pascal',{stage:6,n:5,k:2,focus:'theorem'},'This is the binomial theorem. It explains why Pascal’s coefficients also appear in the binomial probability mass function.','normalization-start');
  add('binomial-total-probability',P,'Add all the bar heights','Each count contributes its binomial probability.',R`\sum_{k=0}^{n}P(X=k)=\sum_{k=0}^{n}\binom nk p^kq^{n-k}`,'binomial',{stage:2,n:5,p:.3,focus:'total'},'This sums probabilities, not value times probability. Multiplying each term by k would instead calculate the expectation. The theorem identifies this sum as (p+q) to the nth power.','normalization-start');
  add('binomial-normalization',P,'All binomial probabilities add to one','Substitute q = 1 − p into the binomial theorem.',R`\sum_{k=0}^{n}P(X=k)=(p+q)^n=1`,'binomial',{stage:2,n:5,p:.3,focus:'total'},'The bars cover all mutually exclusive counts. The algebra checks that their total probability is one. In the classroom route, quote the theorem here and keep the Pascal construction for this detailed route.','normalization-start');
  add('fair-sequence-probability',P,'Give each outcome probability one half','Every length-n sequence now has the same probability.',R`\left(\frac12\right)^k\left(\frac12\right)^{n-k}=\frac1{2^n}`,'combinations',{stage:4,n:5,k:2,p:.5,focus:'fair'},'The k success factors and n minus k failure factors together give n factors of one half. First find the probability of one arrangement; next count how many arrangements are favorable.','fair-coin-start');
  add('binomial-fair',P,'Now set p = q = one half','Every ordered success/failure sequence has probability 2⁻ⁿ.',R`P(X=k)=\frac{\textcolor{#eab308}{\binom nk}}{2^n}`,'combinations',{stage:4,n:5,k:2,p:.5,focus:'fair'},'At one half, not just sequences with the same count but all ordered sequences are equally likely. Count favorable sequences and divide by all two-to-the-n sequences.','fair-coin-start');
  add('fair-count-total',P,'Sum the counts before dividing','Pascal row n counts all 2ⁿ binary sequences.',R`\sum_{k=0}^{n}\binom nk=2^n,\qquad\sum_{k=0}^{n}\frac{\binom nk}{2^n}=1`,'pascal',{stage:7,n:5,k:2,focus:'row-total'},'For five trials the row totals thirty-two. This is the binomial theorem with both inputs equal to one, then divided by thirty-two to get probabilities.','fair-coin-start');

  const E = 'Finish the cereal example';
  add('cereal-boxes',E,'Count prizes in fifty cereal boxes','Each box either contains a prize or does not.',R`X=\text{number of boxes containing a prize}`,'cereal',{stage:-1,view:'boxes',boxMode:'closed',n:50,p:.15,k:4,focus:'setup',mode:'none'},'The sample contains fifty boxes. We model the fifty prize records as independent Bernoulli variables with a common probability p. A prize is the success being counted.','cereal-start');
  add('cereal-claim',E,'Translate the company’s claim','At least fifteen percent of boxes contain a prize.',R`\text{claim: }p\ge0.15`,'cereal',{stage:-1,view:'boxes',boxMode:'probability',n:50,p:.15,k:4,focus:'claim',mode:'none'},'The claim concerns the unknown prize probability, not the observed fraction in one sample. The rule on the next hold uses the sample to assess this claim.','cereal-start');
  add('cereal-expected15',E,'Fifty small chances add to 7.5 expected prizes','At p = 0.15, repeated samples of fifty boxes average 7.5 prizes.',R`E[X]=\underbrace{0.15+\cdots+0.15}_{50\text{ boxes}}=50(0.15)=7.5`,'cereal',{stage:-1,view:'boxes',boxMode:'expectation',n:50,p:.15,k:4,focus:'mean',mode:'none'},'Each unopened box contributes 0.15 to the expected count. The small strips show chances, not partly present prizes. Across repeated samples of fifty boxes, the prize counts average 7.5. Every individual sample still has an integer prize count.','cereal-start');
  add('cereal-rule',E,'Keep the same decision rule','Sample 50 boxes. Reject the “at least 15%” claim when X ≤ 4.',R`\begin{cases}X\le4:&\text{reject the claim},\\X\ge5:&\text{do not reject}.\end{cases}`,'cereal',{stage:0,view:'boxes',boxMode:'expectation',compareCutoff:true,n:50,p:.15,k:4,focus:'rule',mode:'reject'},'Four prizes is below the expected 7.5 at the boundary p=0.15, which motivates using a low count as evidence against the claim. The mean does not uniquely determine the cutoff or its error probability: four is the stated, preselected threshold. Do not reject does not prove the claim true.','cereal-start');
  add('cereal-rule-sample',E,'Four prizes would trigger rejection','This possible sample has four prizes, below the expected count of 7.5.',R`X=4\le4\quad\Longrightarrow\quad\text{reject the claim}`,'cereal',{stage:0,view:'boxes',boxMode:'sample',actualCount:4,compareCutoff:true,n:50,p:.15,k:4,focus:'rule',mode:'reject'},'These fifty pictured boxes are one illustrative sample with four prizes. The actual count is four, while 7.5 is the average across repeated samples when p=0.15. Any count from zero through four triggers the same decision. The binomial calculation will tell us how often these low counts occur when the claim is true.','cereal-start');
  add('cereal-false-reject-sum',E,'Add the rejection bars when p = 0.15','The shaded counts run from zero through four.',R`P_{0.15}(X\le4)=\sum_{k=0}^{4}\binom{50}{k}(0.15)^k(0.85)^{50-k}`,'cereal',{stage:1,n:50,p:.15,k:4,focus:'left-tail',mode:'reject'},'At the boundary p=0.15, the claim is true. A rejection is therefore an error. Add the probabilities of the five counts that trigger rejection.','cereal-start');
  add('cereal-false-reject',E,'Recall the first error','At the boundary p = 0.15, the claim is true.',R`P_{0.15}(X\le4)\approx0.1121`,'cereal',{stage:1,n:50,p:.15,k:4,focus:'left-tail',mode:'reject'},'This is false rejection under the assumed true rate 0.15. The shaded bars are zero through four. Higher true rates make this low-count error less likely.','cereal-start');
  add('cereal-rate-reference',E,'Return to the fifty boxes before changing p','Keep the sample size and the cutoff fixed; first recall the mean at fifteen percent.',R`p=0.15,\qquad E[X]=50(0.15)=7.5`,'cereal',{stage:2,view:'boxes',boxMode:'expectation',compareCutoff:true,n:50,p:.15,k:4,focus:'mean',mode:'none'},'Return to the same unopened-box picture. The gold marker is an expected count across repeated samples. The white cutoff is the fixed decision rule. In the next step only the true prize probability changes.','wed-start');
  add('cereal-truth-changes',E,'Change the assumed truth to five percent','At p = 0.05, fifty boxes average 2.5 prizes; the cutoff is still four.',R`p=0.05,\qquad E[X]=50(0.05)=2.5`,'cereal',{stage:2,view:'boxes',boxMode:'expectation',compareCutoff:true,n:50,p:.05,k:4,focus:'mean',mode:'none'},'Now the company claim is false. Each box has a five-percent prize chance, so the expected count moves from 7.5 to 2.5. The sample size and rejection cutoff stay fixed. The expected count is an average, not a guarantee that one sample contains two or three prizes.','wed-start');
  add('cereal-error-event',E,'Which outcome misses the false claim?','We miss it whenever the rule says “do not reject.”',R`\{\text{miss the false claim}\}=\{X>4\}=\{X\ge5\}`,'cereal',{stage:3,n:50,p:.05,k:4,focus:'right-tail',mode:'miss'},'Ask students to identify the correct tail before showing the sum. Since X is an integer, greater than four means at least five.','wed-start');
  add('cereal-complement',E,'Use the complement of the shaded tail','The counts zero through four cover everything outside it.',R`P_{0.05}(X\ge5)=1-P_{0.05}(X\le4)`,'cereal',{stage:4,n:50,p:.05,k:4,focus:'right-tail',mode:'miss'},'This is one minus the probability of rejecting under the new true rate. We have not changed the decision rule.','wed-start');
  add('cereal-miss-sum',E,'Substitute the five binomial probabilities','Only the true prize probability changed.',R`P_{0.05}(X\ge5)=1-\sum_{k=0}^{4}\binom{50}{k}(0.05)^k(0.95)^{50-k}`,'cereal',{stage:4,n:50,p:.05,k:4,focus:'right-tail',mode:'miss'},'Inside the sum, each term uses p=0.05 and q=0.95. The cutoff remains four, and the sample size remains fifty.','wed-start');
  add('cereal-miss',E,'Interpret the result','The rule misses the false claim about 10.36% of the time.',R`P_{0.05}(X\ge5)\approx\boxed{0.1036}`,'cereal',{stage:4,n:50,p:.05,k:4,focus:'right-tail',mode:'miss'},'At a true prize rate of five percent, this fixed rule misses the false claim about 10.36 percent of the time over repeated samples.','wed-start');
  add('cereal-miss-boxes',E,'What does missing the claim look like in fifty boxes?','Five prizes are shown; every count from five through fifty leads to the same missed rejection.',R`E[X]=2.5,\qquad X\ge5\quad\Longrightarrow\quad\text{do not reject}`,'cereal',{stage:5,view:'boxes',boxMode:'sample',actualCount:5,compareCutoff:true,n:50,p:.05,k:4,focus:'interpretation',mode:'miss'},'This illustrative sample has five prizes, even though the true rate is only five percent and the expected count is 2.5. Five exceeds the fixed cutoff of four, so the rule does not reject the false claim. The 10.36-percent result covers all counts from five through fifty, not just the pictured count of five. Failing to reject does not establish that the company claim is true.','wed-start');
  add('cereal-two-errors',E,'The two errors use different true rates','They are not complementary probabilities.',R`\begin{aligned}p=0.15:&\quad P(X\le4)\approx0.1121\\p=0.05:&\quad P(X\ge5)\approx0.1036\end{aligned}`,'cereal',{stage:5,n:50,p:.05,k:4,focus:'comparison',mode:'miss'},'One probability uses p equal to 0.15; the other uses p equal to 0.05. They come from different distributions, so they need not add to one.','wed-start');
  add('cereal-mean-cutoff',E,'A mean is not a decision cutoff','The mean is 2.5 at p = 0.05; the rule still rejects counts through 4.',R`E[X]=50(0.05)=2.5,\qquad\{X\ge5\}\ne\{X>E[X]\}`,'cereal',{stage:6,view:'boxes',boxMode:'expectation',compareCutoff:true,n:50,p:.05,k:4,focus:'mean',mode:'miss'},'Counts three and four are above the mean but still trigger rejection. Use the stated cutoff when identifying the event.','binomial-moments');
  add('cereal-cutoff-false',E,'Make rejection harder: change the cutoff to three','At p = 0.15, the false-rejection region loses the X = 4 bar.',R`\begin{aligned}P_{0.15}(X\le3)&=\sum_{k=0}^{3}\binom{50}{k}(0.15)^k(0.85)^{50-k}\\&\approx0.0460466.\end{aligned}`,'cereal',{stage:7,n:50,p:.15,k:3,cutoff:3,focus:'left-tail',mode:'reject'},'Change only the decision rule: reject when X is at most three, and do not reject when X is at least four. At the boundary of the true claim, the false-rejection probability decreases from 0.1121052 to 0.0460466. The removed probability is exactly the old bar at four. This does not by itself make the new rule universally better; we must also examine its behavior when the claim is false.','wed-start');
  add('cereal-cutoff-miss',E,'The same cutoff change makes a false claim easier to miss','At p = 0.05, the do-not-reject region gains the X = 4 bar.',R`\begin{aligned}P_{0.05}(X\ge4)&=1-\sum_{k=0}^{3}\binom{50}{k}(0.05)^k(0.95)^{50-k}\\&\approx0.239592.\end{aligned}`,'cereal',{stage:8,n:50,p:.05,k:3,cutoff:3,focus:'right-tail',mode:'miss'},'Keep the new cutoff of three but change the assumed true prize rate to five percent. Now a count of four no longer leads to rejection. It joins the outcomes that miss the false claim, increasing that error from 0.1036168 to 0.2395920. A stricter requirement for rejecting the claim reduces one error but increases the other. The two probabilities still refer to different assumed true rates.','wed-start');

  const M = 'Binomial moments';
  add('binomial-bernoulli-sum',M,'Count prizes by adding Bernoulli variables','Each Iᵢ is one for a prize and zero otherwise.',R`I_i\sim\operatorname{Bernoulli}(p),\qquad X=\sum_{i=1}^{n}I_i`,'sequence',{stage:1,n:50,p:.05,displayCount:10,k:1,sample:[0,0,0,1,0,0,0,0,0,0],focus:'sum'},'These zero-or-one Bernoulli variables are also called indicators. Their sum across all fifty boxes equals X. The picture shows only the first ten records so the full sum remains readable.','binomial-moments');
  add('binomial-mean',M,'Expectations add','Linearity of expectation does not require independence.',R`E[X]=\sum_{i=1}^{n}E[I_i]=\underbrace{p+\cdots+p}_{n\text{ terms}}=\textcolor{#eab308}{n}\textcolor{#a855f7}{p}`,'sequence',{stage:2,n:50,p:.05,displayCount:10,k:1,sample:[0,0,0,1,0,0,0,0,0,0],focus:'mean'},'For the cereal example the means are fifty times 0.15 equals 7.5, or fifty times 0.05 equals 2.5. Independence was not needed to add expectations.','binomial-moments');
  add('binomial-variance-sum',M,'Independent trial variances add','Each Bernoulli variance is pq.',R`\operatorname{Var}(X)=\sum_{i=1}^{n}\operatorname{Var}(I_i)=\underbrace{pq+\cdots+pq}_{n\text{ terms}}=npq`,'sequence',{stage:3,n:50,p:.05,displayCount:10,k:1,sample:[0,0,0,1,0,0,0,0,0,0],focus:'variance'},'For this variance step we do use independence. In general the variance of a sum also has covariance terms; independent trials make those terms zero.','binomial-moments');
  add('binomial-moments',M,'Keep the two formulas together','Binomial: fixed n, common p, independent trials.',R`E[X]=\textcolor{#eab308}{n}\textcolor{#a855f7}{p},\qquad\operatorname{Var}(X)=\textcolor{#eab308}{n}\textcolor{#a855f7}{p}\textcolor{#14b8a6}{q}`,'cereal',{stage:6,n:50,p:.05,k:4,focus:'moments',mode:'none'},'Mean gives the center and variance measures spread. Standard deviation, if wanted, is the square root of npq.','binomial-moments');
  add('binomial-cereal-moments',M,'Apply the moments to the cereal count','At five percent the expected count is 2.5.',R`E[X]=50(0.05)=2.5,\qquad\operatorname{Var}(X)=50(0.05)(0.95)=2.375`,'cereal',{stage:6,n:50,p:.05,k:4,focus:'moments',mode:'miss'},'The distribution can have a noninteger mean even though every realized count is an integer.','binomial-moments');

  const F = 'Why independence changes the variance';
  add('independence-picture',F,'Look at two independent fair trials','Four pairs of outcomes are equally likely.','','foundations',{mode:'independence',stage:0,focus:'all'},'The rows record the first Bernoulli trial; the columns record the second. Each of the four pairs has probability one quarter. We will learn the first outcome and watch what happens to the second.','independence-start');
  add('independence-learn-first',F,'Learn that the first trial succeeded','The second trial still has two equally likely outcomes.',R`P(I_2=1\mid I_1=1)=\frac12=P(I_2=1)`,'foundations',{mode:'independence',stage:1,focus:'given'},'We restrict attention to the row where the first trial succeeded. One of the two remaining equally likely cells has second-trial success. Learning the first outcome did not change that chance.','independence-start');
  add('independence-joint',F,'State this for every pair of values','Independence means the joint probability factors.',R`P(X=x,Y=y)=P(X=x)P(Y=y)`,'foundations',{mode:'independence',stage:0,focus:'all'},'The equality must hold for every pair of values, not merely one pair. A probability describing one variable on its own is called a marginal probability. Independence describes information in a probability distribution; it is not by itself a causal statement.','independence-start');
  add('independence-conditional',F,'Divide by the probability of what we learned','When P(X = x) is positive, the conditional chance stays unchanged.',R`P(Y=y\mid X=x)=\frac{P(X=x)P(Y=y)}{P(X=x)}=P(Y=y)`,'foundations',{mode:'independence',stage:1,focus:'given'},'Conversely, if this conditional distribution is unchanged for every possible x, multiplying by P(X=x) gives the joint factorization. If P(X=x)=0, every joint probability with that x is zero.','independence-start');
  add('linearity-picture',F,'Adding records adds their averages','This rule does not require independence.',R`E[X+Y]=E[X]+E[Y]`,'foundations',{mode:'independence',stage:0,focus:'sum'},'Think of averaging the X+Y column of an outcome table. It is the same as averaging the X column and the Y column separately, using the same probability weights.','independence-start');
  add('linearity-joint-sum',F,'Write that weighted average over the pairs','Use the actual joint probabilities, even when the variables depend.',R`E[X+Y]=\sum_x\sum_y(x+y)P(X=x,Y=y)`,'foundations',{mode:'independence',stage:0,focus:'sum'},'The four-cell picture is an example. The displayed formula works for any discrete outcome table for which the expectations exist.','independence-start');
  add('linearity-collect',F,'Collect each column’s contribution','Summing over the other variable recovers its probability on its own.',R`\begin{aligned}E[X+Y]&=\sum_x xP(X=x)\\&\quad+\sum_y yP(Y=y).\end{aligned}`,'foundations',{mode:'independence',stage:0,focus:'sum'},'For each fixed x, summing P(X=x,Y=y) over y gives P(X=x). The corresponding row sum gives P(Y=y). We have added probabilities, not factored them.','independence-start');
  add('linearity-general',F,'Constants can be carried through the average','Dependence still places no restriction on this addition rule.',R`E[aX+bY+c]=aE[X]+bE[Y]+c`,'foundations',{mode:'independence',stage:0,focus:'sum'},'The same statement holds even if X and Y are the same random variable. For example E[X+X]=2E[X]. We assume the needed expectations exist.','independence-start');
  add('product-start',F,'A product starts with a different average','Multiply the two recorded values within each outcome.',R`E[XY]=\sum_x\sum_y xyP(X=x,Y=y)`,'foundations',{mode:'independence',stage:0,focus:'product'},'This is the definition of the expected product. To separate the two sums, we need an additional property.','independence-start');
  add('product-factor',F,'Now use independence','The probability factors, so the two sums separate.',R`E[XY]=\left(\sum_x xP(X=x)\right)\left(\sum_y yP(Y=y)\right)`,'foundations',{mode:'independence',stage:0,focus:'product'},'Replace the joint probability by the product of its marginal probabilities. Finite second moments justify the rearrangement; in particular 2|XY| is at most X squared plus Y squared.','independence-start');
  add('product-result',F,'Recognize the two expectations','Independence is sufficient for this product rule.',R`E[XY]=E[X]E[Y]`,'foundations',{mode:'independence',stage:0,focus:'product'},'This equality alone does not establish independence. It checks one average, whereas independence checks every pair of possible values. We will see a counterexample.','independence-start');
  add('covariance-center',F,'Measure departures from the two means','Call these centered deviations A and B.',R`A=X-E[X],\qquad B=Y-E[Y]`,'foundations',{mode:'deviations',stage:0,focus:'center'},'Each deviation is positive above its own mean and negative below it. Its expectation is zero. The means are fixed numbers, so subtracting them does not alter independence.','independence-start');
  add('covariance-definition',F,'Average the product of the deviations','Same signs reinforce; opposite signs offset.',R`\operatorname{Cov}(X,Y)=E[AB]`,'foundations',{mode:'deviations',stage:0,focus:'product'},'Covariance is positive when the product of deviations is positive on average, and negative when it is negative on average. Zero covariance permits positive and negative products to cancel.','independence-start');
  add('covariance-expand',F,'Expand before taking the average','Use μX and μY for the two fixed means.',R`E[AB]=E[XY-\mu_YX-\mu_XY+\mu_X\mu_Y]`,'foundations',{mode:'deviations',stage:0,focus:'expand'},'The means can be pulled outside expectation by linearity. The two middle terms each average to minus mu_X mu_Y.','independence-start');
  add('covariance-compute',F,'The means simplify the expression','This identity needs no independence.',R`\operatorname{Cov}(X,Y)=E[XY]-E[X]E[Y]`,'foundations',{mode:'deviations',stage:0,focus:'result'},'This formula turns a covariance into an expected product minus the product of the means. It will be used for the finite-population Bernoulli variables.','independence-start');
  add('variance-square',F,'The sum’s deviation is A + B','Square that sum to measure its variation.',R`\operatorname{Var}(X+Y)=E[(A+B)^2]`,'foundations',{mode:'square',stage:1,focus:'square'},'The area picture illustrates the algebra using positive side lengths. The identity itself also holds when either deviation is negative.','independence-start');
  add('variance-cross-term',F,'The expansion contains two cross terms','Both rectangles contribute AB.',R`(A+B)^2=A^2+\textcolor{#eab308}{2AB}+B^2`,'foundations',{mode:'square',stage:2,focus:'cross'},'The two squares supply A squared and B squared. The two off-diagonal rectangles supply AB twice. This is the extra term that is lost if we add variances too soon.','independence-start');
  add('variance-average-square',F,'Average all three terms','Linearity allows us to average them separately.',R`E[(A+B)^2]=E[A^2]+2E[AB]+E[B^2]`,'foundations',{mode:'square',stage:2,focus:'cross'},'The squared deviations average to the two variances. The product of deviations averages to the covariance.','independence-start');
  add('variance-general-sum',F,'Name the three averages','Dependence appears through the covariance term.',R`\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y)`,'foundations',{mode:'square',stage:2,focus:'cross'},'For dependent variables this term may be positive, negative, or zero. This is the general variance-of-a-sum identity when the variances exist.','independence-start');
  add('variance-independent-cross',F,'Independent deviations have zero expected product','Both centered means are zero.',R`E[AB]=E[A]E[B]=0`,'foundations',{mode:'square',stage:2,focus:'independent'},'The expected product factors because the variables are independent. We did not use symmetry. With covariance zero the sum variance is the sum of the variances.','independence-start');
  add('variance-difference',F,'Subtraction changes the cross-term sign','The two individual variances still add.',R`\operatorname{Var}(X-Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)-2\operatorname{Cov}(X,Y)`,'foundations',{mode:'deviations',stage:2,focus:'difference'},'Expand (A-B) squared. The squared terms remain positive. If X and Y are independent, the covariance vanishes here too, so the variance of their difference is the sum of their variances.','independence-start');
  add('zero-covariance-picture',F,'Zero covariance can still hide a relationship','Choose −1, 0, or 1 equally; then square it.','','foundations',{mode:'dependent',stage:0,focus:'x'},'There are three equally likely joint outcomes: (-1,1), (0,0), and (1,1). Set Y=X squared. Knowing X therefore determines Y.','independence-start');
  add('zero-covariance-means',F,'Average the two columns separately','The X values cancel; two of the Y values equal one.',R`E[X]=0,\qquad E[Y]=\frac23`,'foundations',{mode:'dependent',stage:1,focus:'y'},'Each row has probability one third. The first column averages to zero; the second averages to two thirds.','independence-start');
  add('zero-covariance-product',F,'The products cancel too','The product column is −1, 0, 1.',R`E[XY]=0,\qquad\operatorname{Cov}(X,Y)=0-0\left(\frac23\right)=0`,'foundations',{mode:'dependent',stage:2,focus:'product'},'Positive and negative products cancel exactly. Nevertheless the full joint distribution does not factor.','independence-start');
  add('zero-covariance-dependent',F,'Learning X changes the distribution of Y','When X is zero, Y is certainly zero.',R`P(Y=0\mid X=0)=1\ne\frac13=P(Y=0)`,'foundations',{mode:'dependent',stage:3,focus:'zero-given'},'This single changed conditional probability disproves independence. Zero covariance, product factorization of expectations, and variance additivity are equivalent for this pair, but none guarantees independence.','independence-start');
  add('symmetric-dependent',F,'Zero means and symmetry are not enough','Let A be equally likely −1 or 1, and let B = A.',R`E[A]=E[B]=0,\qquad AB=1`,'foundations',{mode:'copies',stage:1,focus:'same'},'The two values always have the same sign. Their expected product is one despite both means being zero and both distributions being symmetric. For arbitrary U,V, E[UV]=Cov(U,V)+E[U]E[V]; an expected product of zero requires those two terms to cancel.','independence-start');
  add('many-variable-variance',F,'Every distinct pair contributes a cross term','Count each unordered pair once, then multiply by two.',R`\operatorname{Var}\!\left(\sum_i X_i\right)=\sum_i\operatorname{Var}(X_i)+2\sum_{i<j}\operatorname{Cov}(X_i,X_j)`,'sequence',{stage:3,n:5,p:.3,k:2,sample:[1,0,0,1,0],dependent:true,focus:'pairs'},'Pairwise zero covariance is sufficient for variance additivity; pairwise independence is sufficient as well. For three or more variables, a zero total covariance contribution does not imply every pair covariance is zero: different pairs may cancel.','independence-start');
  add('independent-copies',F,'Two independent copies supply two variances','Each copy has variance σ².',R`\operatorname{Var}(X_1+X_2)=2\sigma^2`,'foundations',{mode:'copies',stage:0,focus:'independent'},'The copies have the same distribution but are independent observations. Their covariance is zero.','independence-start');
  add('same-variable-twice',F,'Doubling one variable doubles every deviation','Squaring the doubled deviation multiplies its variance by four.',R`\operatorname{Var}(2X)=4\sigma^2`,'foundations',{mode:'copies',stage:1,focus:'same'},'Adding X to itself is not adding independent copies. Cov(X,X)=Var(X), so the extra covariance term contributes the other two sigma squared.','independence-start');


  const W = 'Change the sampling rule';
  add('replacement-return',W,'With replacement: return the object','N is the total number of objects; K is the number of successes.',R`P(\text{success next draw})=\frac KN=p`,'urn',{stage:0,N:10,K:5,n:3,k:2,p:.5,mode:'replacement',focus:'return'},'Assume a fresh uniform random draw after replacement and mixing. No earlier selection changes the available objects, so the draws are independent.','replacement-start');
  add('replacement-binomial',W,'With replacement gives a binomial count','Keep the population composition and number of draws fixed.',R`X\sim\operatorname{Bin}\!\left(n,\frac KN\right)`,'urn',{stage:1,N:10,K:5,n:3,k:2,p:.5,mode:'replacement',focus:'count'},'A success can be the same physical object selected again. The count is the number of successful draws, not the number of distinct successful objects.','replacement-start');
  add('without-remove',W,'Without replacement: leave the object out','Sᵢ means success on draw i. A first success leaves K − 1 among N − 1.',R`P(S_2\mid S_1)=\frac{K-1}{N-1}`,'urn',{stage:2,N:10,K:5,n:3,k:2,p:.5,mode:'without',focus:'remove-success'},'A success removed leaves one fewer success and one fewer object. Watch only that change first.','replacement-start');
  add('without-failure',W,'Removing a failure changes the chance differently','There are still K successes, but only N − 1 objects.',R`P(S_2\mid S_1^c)=\frac K{N-1}`,'urn',{stage:3,N:10,K:5,n:3,k:2,p:.5,mode:'without',focus:'remove-failure'},'This differs from the case where the first draw succeeded. Knowing an earlier outcome changes later probabilities, so the draws are dependent.','replacement-start');
  add('without-new-count',W,'The count now has a different distribution','We count successes in a uniform sample without replacement.',R`X\sim\operatorname{Hypergeometric}(N,K,n)`,'urn',{stage:4,N:250,K:50,n:12,k:6,p:.2,mode:'without',focus:'population'},'We will count unordered samples. Under uniform sampling without replacement, every subset of n distinct objects is equally likely.','hypergeometric-start');

  const H = 'Skittles: count without replacement';
  add('skittles-population',H,'Identify the whole population','There are 250 Skittles: 50 purple and 200 not purple.',R`N=250,\qquad\textcolor{#a855f7}{K=50},\qquad\textcolor{#14b8a6}{N-K=200}`,'urn',{stage:0,N:250,K:50,n:12,k:6,p:.2,mode:'without',focus:'population'},'Purple is our success category. Every other color belongs to the single failure category. The actual Skittles are distinct objects even when they share a color.','hypergeometric-start');
  add('skittles-sample',H,'Specify the sample and the desired count','Draw 12 without replacement; want exactly 6 purple.',R`\textcolor{#eab308}{n=12},\qquad\textcolor{#a855f7}{k=6},\qquad\textcolor{#14b8a6}{n-k=6}`,'urn',{stage:1,N:250,K:50,n:12,k:6,p:.2,mode:'without',focus:'sample'},'Distinguish K, the successes in the population, from k, the successes in the sample. The question asks for half of the sample to be purple.','hypergeometric-start');
  add('hypergeometric-denominator',H,'First count every possible sample','Choose 12 distinct Skittles from all 250.',R`\text{all samples}=\textcolor{#eab308}{\binom{250}{12}}`,'hypergeom',{stage:0,N:250,K:50,n:12,k:6,p:.2,focus:'denominator'},'We disregard drawing order. Every twelve-object subset is equally likely, so this is the denominator in favorable over total.','hypergeometric-start');
  add('hypergeometric-success-count',H,'Choose the six purple Skittles','Choose 6 from the 50 available successes.',R`\text{purple choices}=\textcolor{#a855f7}{\binom{50}{6}}`,'hypergeom',{stage:1,N:250,K:50,n:12,k:6,p:.2,focus:'success'},'Only the purple selection moves in this hold. The binomial coefficient counts subsets of actual purple objects.','hypergeometric-start');
  add('hypergeometric-failure-count',H,'Choose the six that are not purple','Choose the remaining 6 from the 200 failures.',R`\text{not-purple choices}=\textcolor{#14b8a6}{\binom{200}{6}}`,'hypergeom',{stage:2,N:250,K:50,n:12,k:6,p:.2,focus:'failure'},'Now focus only on the other-color selection. An exactly-six-purple sample must also contain exactly six nonpurple objects.','hypergeometric-start');
  add('hypergeometric-product',H,'Pair each purple choice with each other-color choice','Multiply to count all favorable samples.',R`\text{favorable samples}=\textcolor{#a855f7}{\binom{50}{6}}\textcolor{#14b8a6}{\binom{200}{6}}`,'hypergeom',{stage:3,N:250,K:50,n:12,k:6,p:.2,focus:'numerator'},'This multiplication is the counting product rule. It does not assert that the individual draws are independent. Every favorable sample has exactly one such pair of subsets.','hypergeometric-start');
  add('hypergeometric-pmf',H,'Divide favorable samples by all samples','The formula keeps the two color selections visible.',R`P(X=k)=\frac{\textcolor{#a855f7}{\binom Kk}\textcolor{#14b8a6}{\binom{N-K}{n-k}}}{\textcolor{#eab308}{\binom Nn}}`,'hypergeom',{stage:4,N:250,K:50,n:12,k:6,p:.2,focus:'pmf'},'The allowable integer values satisfy max of zero and n minus (N minus K), through min of n and K. Impossible selections have probability zero.','hypergeometric-start');
  add('hypergeometric-support',H,'The count must fit both available supplies','We cannot select more successes or failures than the population contains.',R`\max(0,n-(N-K))\le k\le\min(n,K)`,'hypergeom',{stage:4,N:250,K:50,n:12,k:6,p:.2,focus:'support'},'The count k is an integer. The upper bound limits successes by both sample size and population successes. The lower bound ensures enough failures are available for the other n-k selections. Outside these bounds the probability is zero.','hypergeometric-start');
  add('hypergeometric-normalization',H,'Every sample has exactly one success count','Partition all n-object samples according to their number k of successes.',R`\begin{aligned}\sum_k\textcolor{#a855f7}{\binom Kk}\textcolor{#14b8a6}{\binom{N-K}{n-k}}&=\textcolor{#eab308}{\binom Nn},\\\sum_kP(X=k)&=1.\end{aligned}`,'hypergeom',{stage:4,N:250,K:50,n:12,k:6,p:.2,focus:'total'},'The sum runs over all feasible integer success counts. Samples with different values of k cannot overlap, and every n-object sample belongs to exactly one group. Adding the favorable counts for all groups therefore counts all n-object samples once. Divide both sides by N choose n to prove that the hypergeometric probabilities sum to one. This is a counting proof; no assumption of independent draws is used.','hypergeometric-start');
  add('hypergeometric-skittles',H,'Substitute the Skittles numbers','Exactly half purple occurs with probability about 1.376%.',R`P(X=6)=\frac{\textcolor{#a855f7}{\binom{50}{6}}\textcolor{#14b8a6}{\binom{200}{6}}}{\textcolor{#eab308}{\binom{250}{12}}}\approx0.0137602`,'hypergeom',{stage:5,N:250,K:50,n:12,k:6,p:.2,focus:'answer'},'The expected purple fraction is twenty percent, so six purple out of twelve is well above the mean count. The probability calculation quantifies how unusual that particular count is.','hypergeometric-start');

  const G = 'Same chance before seeing the draws';
  add('hypergeometric-bernoullis',G,'The count is still a sum of Bernoulli variables','Use ten labeled objects for the proof: four successes and six failures.',R`I_i\in\{0,1\},\qquad X=\sum_{i=1}^{n}I_i`,'sequence',{stage:0,n:10,p:.4,k:4,sample:[0,1,0,1,0,0,1,0,1,0],focus:'sum'},'Each indicator is just a Bernoulli random variable. The count identity works whether or not the draws are independent.','hypergeometric-moments');
  add('marginal-shuffle',G,'Imagine shuffling the objects into a row','Revealing this random row is sampling without replacement.',R`N=10,\qquad K=4`,'sequence',{stage:1,n:10,p:.4,k:4,sample:[0,1,0,1,0,0,1,0,1,0],focus:'shuffle'},'Use four success objects and six failure objects so students can see the whole population. Before revealing any outcome, imagine a uniformly random permutation of all ten distinct objects.','hypergeometric-moments');
  add('marginal-position',G,'Focus on any one position before revealing it','Every object is equally likely to occupy that position.',R`P(I_i=1)=\frac{\textcolor{#a855f7}{K}}{N}=\frac4{10}`,'sequence',{stage:2,n:10,p:.4,k:4,sample:[0,1,0,1,0,0,1,0,1,0],focus:'position',highlight:[4]},'There is no favored position in a shuffled row. Four of the ten objects are successes, so position five, like position one, has a four-in-ten chance of success before outcomes are observed.','hypergeometric-moments');
  add('marginal-given-success',G,'Learning a success changes the next chance','A first success leaves 3 successes among 9 objects.',R`P(S_2\mid S_1)=\frac39`,'urn',{stage:2,N:10,K:4,n:2,k:2,p:.4,mode:'without',focus:'remove-success'},'This conditional probability uses information we did not have in the shuffled-position question. The population composition after a known success is different.','hypergeometric-moments');
  add('marginal-given-failure',G,'Learning a failure changes it another way','A first failure leaves 4 successes among 9 objects.',R`P(S_2\mid S_1^c)=\frac49`,'urn',{stage:3,N:10,K:4,n:2,k:1,p:.4,mode:'without',focus:'remove-failure'},'Keep the second-draw question fixed and change only what we learned about the first draw.','hypergeometric-moments');
  add('marginal-partition',G,'Without that information, include both cases','The first draw either succeeds or fails.',R`P(S_2)=P(S_1\cap S_2)+P(S_1^c\cap S_2)`,'urn',{stage:4,N:10,K:4,n:2,p:.4,mode:'lotp',focus:'partition'},'These two routes to a second-draw success are disjoint and exhaustive. This is a picture of the law of total probability.','hypergeometric-moments');
  add('marginal-first-success-route',G,'Follow the first-success route','Multiply the first chance by the second chance on this route.',R`P(S_1\cap S_2)=\frac4{10}\cdot\frac39`,'urn',{stage:4,N:10,K:4,n:2,p:.4,mode:'lotp',focus:'branch-success'},'A first success has probability four tenths. Given that success, the second success has probability three ninths. Multiply those two factors.','hypergeometric-moments');
  add('marginal-first-failure-route',G,'Now follow the first-failure route','This route has six possible failures first.',R`P(S_1^c\cap S_2)=\frac6{10}\cdot\frac49`,'urn',{stage:4,N:10,K:4,n:2,p:.4,mode:'lotp',focus:'branch-failure'},'A first failure has probability six tenths. It leaves four successes out of nine. The two routes are disjoint, so we add their probabilities next.','hypergeometric-moments');
  add('marginal-lotp',G,'Weight each conditional chance by its first-draw chance','The weighted average returns to 4/10.',R`P(S_2)=\frac39\cdot\frac4{10}+\frac49\cdot\frac6{10}=\frac4{10}`,'urn',{stage:5,N:10,K:4,n:2,p:.4,mode:'lotp',focus:'weighted'},'Multiply along each route, then add the routes. The answer is exactly the probability predicted by symmetry of positions in the shuffled row.','hypergeometric-moments');
  add('marginal-name',G,'Now give that probability its optional name','A marginal probability describes this draw without conditioning on the other outcomes.',R`\underbrace{P(S_2)}_{\text{marginal}}=\frac4{10},\qquad\underbrace{P(S_2\mid S_1)}_{\text{conditional}}=\frac39`,'urn',{stage:5,N:10,K:4,n:2,p:.4,mode:'lotp',focus:'marginal'},'Introduce the name only after students understand the two questions. Equal marginal success probabilities do not imply independence.','hypergeometric-moments');
  add('hypergeometric-mean',G,'Add the Bernoulli expectations','Every draw has probability p = K/N before conditioning on other draws.',R`E[X]=\sum_{i=1}^{n}E[I_i]=\sum_{i=1}^{n}\frac KN=\textcolor{#eab308}{n}\textcolor{#a855f7}{p}`,'urn',{stage:6,N:250,K:50,n:12,k:6,p:.2,mode:'without',focus:'mean'},'Each I_i is Bernoulli with parameter K over N. Linearity of expectation holds for dependent variables, so the mean still equals np.','hypergeometric-moments');
  add('hypergeometric-mean-skittles',G,'The expected purple count is 2.4','Twelve draws, each with unconditional purple probability 0.2.',R`p=\frac{50}{250}=0.2,\qquad E[X]=12(0.2)=2.4`,'hypergeom',{stage:6,N:250,K:50,n:12,k:6,p:.2,focus:'mean'},'The mean can be noninteger. It describes the long-run average purple count across repeated twelve-object samples with the population restored between samples.','hypergeometric-moments');

  const V = 'Dependence appears in the variance';
  add('variance-covariances',V,'A variance of a sum includes pair terms','Dependence enters through the covariances.',R`\operatorname{Var}(X)=\sum_{i=1}^{n}\operatorname{Var}(I_i)+2\sum_{i<j}\operatorname{Cov}(I_i,I_j)`,'sequence',{stage:3,n:10,p:.4,focus:'pairs'},'Each I_i is a Bernoulli variable, hence has variance pq. The covariance terms record how two different draws vary together. The classroom route only needs the resulting correction factor.','hypergeometric-moments');
  add('variance-joint',V,'The product of two Bernoulli variables detects two successes','IᵢIⱼ equals one exactly when both draws succeed.',R`E[I_iI_j]=P(I_i=1,I_j=1)=\frac KN\frac{K-1}{N-1}\quad(i\ne j)`,'urn',{stage:2,N:10,K:4,n:2,k:2,p:.4,mode:'without',focus:'joint'},'By symmetry we can examine any two distinct positions as the first two positions. To have both successes, select one success then another from the remaining population.','hypergeometric-moments');
  add('variance-covariance',V,'Subtract the product of the means','Each Bernoulli variable has mean K/N.',R`\operatorname{Cov}(I_i,I_j)=\frac{K(K-1)}{N(N-1)}-\frac{K^2}{N^2}`,'urn',{stage:6,N:10,K:4,n:2,p:.4,mode:'without',focus:'covariance'},'Covariance is E[I_i I_j] minus E[I_i] times E[I_j]. The joint-success probability supplies the first fraction, while each Bernoulli mean supplies K over N to the second term. We will simplify this subtraction one operation at a time.','hypergeometric-moments');
  add('variance-common-denominator',V,'Give the two fractions a common denominator','Use N²(N − 1).',R`\operatorname{Cov}(I_i,I_j)=\frac{NK(K-1)-K^2(N-1)}{N^2(N-1)}`,'urn',{stage:6,N:10,K:4,n:2,p:.4,mode:'without',focus:'denominator'},'Multiply the first fraction’s numerator and denominator by N. Multiply the second fraction’s numerator and denominator by N minus one. Because we are subtracting fractions, keep the entire second numerator inside parentheses until it is expanded.','hypergeometric-moments');
  add('variance-numerator',V,'Cancel the matching NK² terms','The numerator becomes −K(N − K).',R`\begin{aligned}NK(K-1)-K^2(N-1)&=NK^2-NK-NK^2+K^2\\&=-K(N-K).\end{aligned}`,'urn',{stage:6,N:10,K:4,n:2,p:.4,mode:'without',focus:'numerator'},'Expand both products carefully, including the minus sign before the second product. The NK squared terms cancel. The terms remaining are K squared minus NK, which factor as minus K times N minus K. Thus the covariance is nonpositive.','hypergeometric-moments');
  add('variance-pq',V,'Recognize the success and failure fractions','K/N is p, and (N − K)/N is q.',R`\operatorname{Cov}(I_i,I_j)=-\frac{\left(\textcolor{#a855f7}{K/N}\right)\left(\textcolor{#14b8a6}{(N-K)/N}\right)}{N-1}=-\frac{\textcolor{#a855f7}{p}\textcolor{#14b8a6}{q}}{N-1}`,'urn',{stage:6,N:10,K:4,n:2,p:.4,mode:'without',focus:'covariance-result'},'This formula applies to two distinct draw positions when N is greater than one. For a population containing both outcomes the covariance is negative: learning that one draw was a success reduces the chance of a success on the other draw. If all objects have the same outcome, p times q is zero and there is no variability.','hypergeometric-moments');
  add('variance-pair-count',V,'Count the pairs once','There are n choose 2 unordered pairs of draws.',R`\operatorname{Var}(X)=npq+2\binom n2\left(-\frac{pq}{N-1}\right)`,'sequence',{stage:4,n:6,p:.4,focus:'pairs'},'The variance expansion already places a factor of two before the unordered-pair sum. Two times n choose two is n times n minus one.','hypergeometric-moments');
  add('hypergeometric-variance',V,'Factor out the binomial variance','The remaining factor accounts for sampling without replacement.',R`\operatorname{Var}(X)=npq\left(1-\frac{n-1}{N-1}\right)=\boxed{npq\frac{N-n}{N-1}}`,'hypergeom',{stage:7,N:250,K:50,n:12,k:6,p:.2,focus:'variance'},'For N greater than one, the correction is at most one. The mean stayed np because expectations add even under dependence. Dependence appears in the variance calculation.','hypergeometric-moments');
  add('hypergeometric-variance-skittles',V,'Evaluate the correction for Skittles','Sampling 12 of 250 gives slightly less spread than replacement.',R`\operatorname{Var}(X)=12(0.2)(0.8)\frac{250-12}{250-1}\approx1.83518`,'hypergeom',{stage:8,N:250,K:50,n:12,k:6,p:.2,focus:'variance'},'With replacement the binomial variance would be 1.92. Without replacement it is about 1.83518. The two counts have the same mean of 2.4.','hypergeometric-moments');
  add('hypergeometric-full-sample',V,'Check the extreme: sample everyone','If n = N, the count must be exactly K.',R`n=N\quad\Longrightarrow\quad X=K,\qquad\operatorname{Var}(X)=0`,'urn',{stage:7,N:20,K:8,n:20,k:8,p:.4,mode:'without',focus:'all'},'The finite population correction becomes zero. There is no randomness left in the number of successes once the entire fixed population has been selected.','hypergeometric-moments');
  add('balanced-population-dependent',V,'Half successes does not imply fair independent trials','Sampling without replacement still reduces the variance.',R`p=\frac12:\quad \operatorname{Var}(X)=\frac n4\frac{N-n}{N-1}`,'urn',{stage:2,N:10,K:5,n:3,k:2,p:.5,mode:'without',focus:'remove-success'},'Each draw has chance one half before observing the other draws. But after a success, only four of nine remaining objects succeed. This differs from independent fair flips.','hypergeometric-start');

  const L = 'A large population approaches replacement';
  add('hyperlimit-small',L,'Hold the sample size fixed','Start with n = 10 from N = 12 and half successes.',R`n=10,\quad p=\frac KN=\frac12,\quad\frac{N-n}{N-1}=\frac2{11}`,'hyperlimit',{stage:0,N:12,K:6,n:10,p:.5,trials:4000,focus:'exact'},'Compare exact hypergeometric bars with exact binomial bars. Sampling almost everyone strongly limits the possible counts and shrinks the variance.','hypergeometric-limit');
  add('hyperlimit-medium',L,'Enlarge only the population','The sample remains ten; the success fraction remains one half.',R`N=40,\quad K=20,\quad n=10,\quad\frac{N-n}{N-1}=\frac{30}{39}`,'hyperlimit',{stage:1,N:40,K:20,n:10,p:.5,trials:4000,focus:'exact'},'Removing a few successes or failures now changes the population fraction less. The two exact distributions are closer.','hypergeometric-limit');
  add('hyperlimit-large',L,'A small sample barely depletes a large population','The correction factor gets close to one.',R`N=400,\quad K=200,\quad n=10,\quad\frac{N-n}{N-1}=\frac{390}{399}`,'hyperlimit',{stage:2,N:400,K:200,n:10,p:.5,trials:4000,focus:'exact'},'Keep n fixed while increasing N. This is a different limiting process from the binomial-to-Poisson limit coming next.','hypergeometric-limit');
  add('hyperlimit-simulation',L,'Compare repeated samples with the exact probabilities','Simulated relative frequencies fluctuate around the exact hypergeometric pmf.',R`\widehat P(X=k)=\frac{\#\{\text{simulated samples with count }k\}}{\text{number of samples}}`,'hyperlimit',{stage:3,N:400,K:200,n:10,p:.5,trials:4000,focus:'simulation'},'Restore the population before each repeated sample. Within a sample, draw without replacement. Simulation illustrates the exact distribution; it does not prove the limit.','simulation-start');
  add('hyperlimit-statement',L,'State what stays fixed in this limit','Fixed n; growing N; population success fraction approaching p.',R`N\to\infty,\quad K/N\to p,\quad n\text{ fixed}:\qquad\operatorname{Hypergeometric}(N,K,n)\longrightarrow\operatorname{Bin}(n,p)`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,trials:4000,focus:'limit'},'As the population grows, a fixed number of draws has negligible effect on its composition. The without-replacement count approaches its with-replacement counterpart.','hypergeometric-limit');
  add('hyperlimit-falling-factorial',L,'Name a descending product before using it','A falling factorial counts ordered selections without replacement.',R`\begin{aligned}(a)_{\underline r}&=a(a-1)\cdots(a-r+1),\\(a)_{\underline0}&=1,\qquad\binom ar=\frac{(a)_{\underline r}}{r!}.\end{aligned}`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,trials:4000,focus:'falling-factorial'},'The underline distinguishes a falling factorial from an ordinary power. For example, ten falling three is ten times nine times eight, whereas ten cubed is ten times ten times ten. Dividing by r factorial forgets the selection order. We use this notation only to make the limit calculation readable.','hypergeometric-limit');
  add('hyperlimit-factorial-grouping',L,'Rewrite the three combinations as descending products','Group n!/[k!(n − k)!] into a binomial coefficient.',R`P(X_N=k)=\textcolor{#eab308}{\binom nk}\frac{\textcolor{#a855f7}{(K_N)_{\underline k}}\textcolor{#14b8a6}{(N-K_N)_{\underline{n-k}}}}{(N)_{\underline n}}`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,trials:4000,focus:'coefficient'},'Let K_N denote the number of successes in the population of size N. Replace K_N choose k, N minus K_N choose n minus k, and N choose n with their falling-factorial formulas. Dividing by the denominator multiplies by n factorial. The three ordinary factorials combine into n choose k. The remaining descending products retain the without-replacement behavior.','hypergeometric-limit');
  add('hyperlimit-scale-factors',L,'Divide the descending products by matching powers of N','The two numerator powers multiply to the denominator power Nⁿ.',R`P(X_N=k)=\binom nk\frac{\displaystyle\frac{(K_N)_{\underline k}}{N^k}\,\frac{(N-K_N)_{\underline{n-k}}}{N^{n-k}}}{\displaystyle\frac{(N)_{\underline n}}{N^n}}`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,trials:4000,focus:'scale'},'This step does not change the probability: the powers cancel because k plus n minus k equals n. It puts each descending product into a form whose factors have simple limits. Keep both the sample size n and the target count k fixed. Assume K_N divided by N tends to an interior success fraction p, with zero less than p less than one.','hypergeometric-limit');
  add('hyperlimit-factor-limits',L,'Take the limit of the success product','There are k factors, each approaching p.',R`\frac{(K_N)_{\underline k}}{N^k}=\prod_{j=0}^{k-1}\left(\frac{K_N}{N}-\frac jN\right)\to p^k`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,trials:4000,focus:'factor-limits'},'For the success product, every factor K_N over N minus j over N approaches p. For the failure product, every factor one minus K_N over N minus j over N approaches one minus p. For the total-population product, every factor one minus j over N approaches one. There are finitely many factors because n and k stay fixed. Empty products equal one, so this also handles k zero or k equal to n.','hypergeometric-limit');
  add('hyperlimit-failure-factors',L,'Take the limit of the failure product','Its n − k factors each approach 1 − p.',R`\frac{(N-K_N)_{\underline{n-k}}}{N^{n-k}}\longrightarrow(1-p)^{n-k}`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,focus:'failure-limit'},'Keep n and k fixed. Every scaled failure factor has form one minus K_N/N minus j/N and approaches one minus p.','hypergeometric-limit');
  add('hyperlimit-total-factors',L,'The denominator approaches one','Each of its n factors approaches one.',R`\frac{(N)_{\underline n}}{N^n}=\prod_{j=0}^{n-1}\left(1-\frac jN\right)\longrightarrow1`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,focus:'total-limit'},'With n fixed, only finitely many factors need to converge. We can now combine the numerator and denominator limits.','hypergeometric-limit');
  add('hyperlimit-pmf-proof',L,'Combine the three limits','The limiting formula is exactly the binomial pmf.',R`P(X_N=k)\longrightarrow\textcolor{#eab308}{\binom nk}\textcolor{#a855f7}{p^k}\textcolor{#14b8a6}{(1-p)^{n-k}},\qquad k=0,\ldots,n`,'hyperlimit',{stage:4,N:400,K:200,n:10,p:.5,k:5,trials:4000,focus:'pmf-proof'},'The denominator tends to one, so taking the quotient is valid. The binomial coefficient does not change because n and k are fixed. For an interior limiting success fraction, both successes and failures are eventually numerous enough to allow every count from zero through n. This exact probability calculation proves the approximation suggested by the pictures and simulations.','hypergeometric-limit');

  const RAIN = 'Many tiny chances → an event count';
  add('poisson-lab-picture',RAIN,'Count rare processing errors','A laboratory processes one thousand specimens.',R`X=\text{number of specimens with an error}`,'binomial',{stage:0,maxK:12,n:1000,p:.002,lambda:2,k:2,focus:'example'},'Assume the specimens experience independent errors with a common probability of 0.002. The exact count is binomial. This concrete rare-event example appears before the general Poisson formula in the notes.','poisson-example');
  add('poisson-lab-exact',RAIN,'Start with the exact binomial model','Many opportunities; a small error chance for each.',R`X\sim\operatorname{Bin}(1000,0.002)`,'binomial',{stage:0,maxK:12,n:1000,p:.002,lambda:2,k:2,focus:'example'},'We can calculate exact binomial probabilities without any approximation. A Poisson approximation is useful when it simplifies the calculation or clarifies the limiting model.','poisson-example');
  add('poisson-lab-zero',RAIN,'No errors means every specimen succeeds in avoiding one','Multiply one thousand no-error probabilities.',R`P(X=0)=(0.998)^{1000}\approx0.135065`,'binomial',{stage:0,maxK:12,n:1000,p:.002,lambda:2,k:0,focus:'example'},'Here success in the Bernoulli coding is an error, because an error is what X counts. The no-error probability on each specimen is 0.998.','poisson-example');
  add('poisson-lab-at-least-one',RAIN,'At least one error is the complement','Subtract the no-error probability from one.',R`P(X\ge1)=1-(0.998)^{1000}\approx0.864935`,'binomial',{stage:0,maxK:12,n:1000,p:.002,lambda:2,k:0,focus:'example'},'The complement avoids adding 1000 separate terms for counts one through 1000.','poisson-example');
  add('poisson-lab-two',RAIN,'Exactly two errors is one binomial term','Choose the two specimens that experience errors.',R`P(X=2)=\binom{1000}{2}(0.002)^2(0.998)^{998}\approx0.270942`,'binomial',{stage:0,maxK:12,n:1000,p:.002,lambda:2,k:2,focus:'example'},'The expected count is np=2 and its variance is np(1-p)=1.996. The Poisson approximation with lambda 2 has nearly the same mean and variance.','poisson-example');
  add('poisson-lab-fixed-mean',RAIN,'Increase opportunities while making each error rarer','Both experiments have expected count two.',R`1000(0.002)=2000(0.001)=2`,'poissonlimit',{stage:0,n:2000,p:.001,lambda:2,k:2,focus:'mean'},'This change illustrates what stays fixed in the limit: the expected count np. Increasing the number of opportunities with p fixed would instead increase the mean.','poisson-example');
  add('poisson-rain-picture',RAIN,'Count raindrops in a fixed window','Choose an area and an observation time before counting.',R`X=\text{number of drops landing in the selected area and time}`,'rain',{stage:0,rate:300,area:1,seconds:.01,lambda:3,focus:'window'},'A raindrop count is a discrete random variable because its possible values are nonnegative integers. Being a count alone does not establish a Poisson model.','poisson-exposure');
  add('poisson-assumptions',RAIN,'Specify the event model','Use an approximately constant rate and independent counts in disjoint windows.',R`X\sim\operatorname{Poisson}(\lambda)\quad\text{under the Poisson model}`,'rain',{stage:1,rate:300,area:1,seconds:.01,lambda:3,focus:'independence'},'For a homogeneous Poisson model, sufficiently small windows have very small probabilities of multiple events, and nonoverlapping windows have independent counts. Real rainfall need not satisfy this exactly; this is the stated model for the example.','poisson-exposure');
  add('poisson-tiny-opportunities',RAIN,'Divide the window into many tiny pieces','In a tiny piece, “one event” is a rare success.',R`n\text{ large},\qquad p\text{ small},\qquad np\approx\lambda`,'rain',{stage:2,rate:300,area:1,seconds:.01,lambda:3,n:50,p:.06,focus:'cells'},'The binomial analogy uses many independent small opportunities with a small event probability. The expected total count is the number of opportunities times their success probability.','poisson-example');
  add('poisson-lambda',RAIN,'Keep the expected total count fixed','λ belongs to the chosen observation window.',R`\textcolor{#38bdf8}{\lambda}=np\quad\text{(binomial approximation)}`,'poissonlimit',{stage:0,n:50,p:.06,lambda:3,trials:4000,focus:'mean'},'The parameter lambda is an expected count. A rate per unit time or area must be multiplied by the window’s exposure to obtain lambda.','poisson-example');
  add('poisson-rate',RAIN,'Start with the rainfall rate','Three hundred drops per square foot per second.',R`\rho=300\ \frac{\text{drops}}{\mathrm{ft}^2\,\mathrm{s}}`,'rain',{stage:2,rate:300,area:1,seconds:.01,lambda:3,focus:'rate'},'A rate is not yet the Poisson parameter. We must specify the area and duration over which events are counted.','poisson-exposure');
  add('poisson-exposure-window',RAIN,'Choose the area and duration','Watch one square foot for one hundredth of a second.',R`A=1\,\mathrm{ft}^2,\qquad t=0.01\,\mathrm{s}`,'rain',{stage:2,rate:300,area:1,seconds:.01,lambda:3,focus:'exposure-window'},'Keep the stated rate fixed. Now define the exposure before calculating the mean count.','poisson-exposure');
  add('poisson-rate-units',RAIN,'Convert the rainfall rate into a mean count','Rate × area × time gives the expected number of drops.',R`\textcolor{#38bdf8}{\lambda}=\rho At=300(1)(0.01)=3`,'rain',{stage:3,rate:300,area:1,seconds:.01,lambda:3,focus:'units'},'The stated rate is three hundred drops per square foot per second. Over one square foot for one hundredth of a second, the expected count is three. Units cancel to a count.','poisson-exposure');
  add('poisson-pmf',RAIN,'Assign a probability to each integer count','The Poisson pmf has one parameter: the expected count λ.',R`P(X=k)=e^{-\textcolor{#38bdf8}{\lambda}}\frac{\textcolor{#38bdf8}{\lambda}^{\textcolor{#eab308}{k}}}{\textcolor{#eab308}{k!}},\qquad k=0,1,2,\ldots`,'poisson',{stage:0,lambda:3,k:2,focus:'pmf'},'Unlike a binomial count, the Poisson model has no fixed finite maximum count. Its support is all nonnegative integers.','poisson-start');
  add('poisson-support',RAIN,'A count remains discrete','Each bar belongs to one nonnegative integer.',R`X\in\{0,1,2,3,\ldots\}`,'poisson',{stage:1,lambda:3,focus:'support'},'The chart is a probability mass function. A finite display omits a small upper tail; it does not truncate the mathematical distribution.','poisson-start');

  const PL = 'Derive the Poisson limit';
  add('poissonlimit-set-p',PL,'Begin with a binomial count and set p = λ/n','Increasing n then makes p smaller while keeping np = λ.',R`X_n\sim\operatorname{Bin}\!\left(n,\frac\lambda n\right),\qquad np=\lambda`,'poissonlimit',{stage:0,n:10,p:.3,lambda:3,k:2,trials:4000,focus:'mean'},'Take n large enough that lambda over n is a valid probability. We study each fixed integer k as n grows.','poisson-limit');
  add('poissonlimit-substitute',PL,'Substitute into the binomial pmf','Keep the target count k fixed.',R`P(X_n=k)=\binom nk\left(\frac\lambda n\right)^k\left(1-\frac\lambda n\right)^{n-k}`,'poissonlimit',{stage:1,n:10,p:.3,lambda:3,k:2,trials:4000,focus:'pmf'},'The equation still gives an exact binomial probability at every finite n. The approximation appears when we replace it by its limit.','poisson-limit');
  add('poissonlimit-expand-count',PL,'Expand only the counting coefficient','Cancel the nᵏ from the success-probability factors.',R`\binom nk\left(\frac\lambda n\right)^k=\frac{\lambda^k}{k!}\prod_{j=0}^{k-1}\left(1-\frac jn\right)`,'poissonlimit',{stage:2,n:50,p:.06,lambda:3,k:2,trials:4000,focus:'coefficient'},'Write the numerator of n choose k as n times n minus one through n minus k plus one. Divide each factor by n. For k zero, use the empty-product value one.','poisson-limit');
  add('poissonlimit-count-limit',PL,'Each of those finitely many factors approaches one','This leaves λᵏ/k!.',R`\prod_{j=0}^{k-1}\left(1-\frac jn\right)\longrightarrow1`,'poissonlimit',{stage:3,n:50,p:.06,lambda:3,k:2,trials:4000,focus:'coefficient'},'The number k of factors is fixed in this limit. This is how the counting term in the binomial pmf becomes the factorial term in the Poisson pmf.','poisson-limit');
  add('poissonlimit-count-result',PL,'Keep the factor left outside that product','The success and counting part approaches λᵏ/k!.',R`\binom nk\left(\frac\lambda n\right)^k\longrightarrow\frac{\lambda^k}{k!}`,'poissonlimit',{stage:3,n:50,p:.06,lambda:3,k:2,focus:'coefficient'},'We have taken the limit of one part of the probability. The failure factors still need their own limit.','poisson-limit');
  add('poissonlimit-failure-limit',PL,'Now take the limit of the failure factors','The exponential supplies e⁻λ.',R`\left(1-\frac\lambda n\right)^{n-k}=\frac{\left(1-\lambda/n\right)^n}{\left(1-\lambda/n\right)^k}`,'poissonlimit',{stage:4,n:500,p:.006,lambda:3,k:2,trials:4000,focus:'exponential'},'Use the standard exponential limit for the first factor. The second factor approaches one because k is fixed.','poisson-limit');
  add('poissonlimit-exponential',PL,'Apply the exponential limit','The numerator approaches e⁻λ; the denominator approaches one.',R`\left(1-\frac\lambda n\right)^{n-k}\longrightarrow e^{-\lambda}`,'poissonlimit',{stage:4,n:500,p:.006,lambda:3,k:2,focus:'exponential'},'The standard limit is (1-lambda/n) to the n tending to exp(-lambda). The fixed kth power in the denominator tends to one.','poisson-limit');
  add('poissonlimit-result',PL,'Combine the two limits','Binomial probabilities approach the Poisson pmf.',R`P(X_n=k)\longrightarrow e^{-\lambda}\frac{\lambda^k}{k!}`,'poissonlimit',{stage:5,n:500,p:.006,lambda:3,k:2,trials:4000,focus:'limit'},'More generally, the same limit holds when n tends to infinity, p tends to zero, and np tends to a finite positive lambda.','poisson-limit');
  add('poissonlimit-compare',PL,'Compare n = 10, 50, and 500 at the same mean','The binomial variance approaches λ as p shrinks.',R`E[X_n]=\lambda,\qquad\operatorname{Var}(X_n)=\lambda\left(1-\frac\lambda n\right)\longrightarrow\lambda`,'poissonlimit',{stage:6,n:500,p:.006,lambda:3,trials:4000,focus:'moments'},'For lambda three, the corresponding p values are 0.3, 0.06, and 0.006. The exact distributions become close; the limiting moment formulas motivate, but do not replace, the direct proofs below.','poisson-limit');
  add('poissonlimit-simulation',PL,'Let repeated experiments illustrate the limiting shape','Compare simulation frequencies with exact binomial and Poisson probabilities.',R`\widehat P(X_n=k)=\frac{\#\{\text{simulated counts equal }k\}}{\text{number of experiments}}`,'poissonlimit',{stage:7,n:500,p:.006,lambda:3,trials:4000,focus:'simulation'},'Each simulated binomial experiment uses n independent Bernoulli trials with p equal to lambda over n. Simulation variation is not a disagreement with the exact pmf and is not a proof of convergence.','poisson-limit');
  add('poisson-source-comparison',PL,'Approximation does not mean exact equality','The notes also compare n = 100, p = 0.05 with λ = 5.',R`\begin{aligned}P_{\operatorname{Bin}(100,.05)}(X=2)&\approx0.08118,\\P_{\operatorname{Poisson}(5)}(X=2)&\approx0.08422.\end{aligned}`,'poissonlimit',{stage:6,n:100,p:.05,lambda:5,k:2,focus:'example'},'The exact binomial and approximate Poisson models share expected count five. The closeness varies with the parameters and the event being estimated. Use the exact binomial when it is convenient.','poisson-limit');

  const PM = 'Prove the Poisson formulas';
  add('poisson-series',PM,'Recall the exponential series','Use the same series with input λ.',R`e^\lambda=\sum_{k=0}^{\infty}\frac{\lambda^k}{k!}`,'poisson',{stage:2,lambda:3,focus:'series'},'This series identity is the algebraic tool for checking total probability and the two moments.','poisson-start');
  add('poisson-normalization',PM,'The probabilities sum to one','Factor out e⁻λ and recognize the exponential series.',R`\sum_{k=0}^{\infty}P(X=k)=e^{-\lambda}\sum_{k=0}^{\infty}\frac{\lambda^k}{k!}=e^{-\lambda}e^\lambda=1`,'poisson',{stage:3,lambda:3,focus:'total'},'Every term is nonnegative, and the full infinite series totals one.','poisson-start');
  add('poisson-mean-start',PM,'Start the expectation from its definition','The k = 0 term contributes zero.',R`E[X]=\sum_{k=1}^{\infty}k\,e^{-\lambda}\frac{\lambda^k}{k!}`,'poisson',{stage:4,lambda:3,focus:'mean'},'Multiply each possible count by its probability. We may start at one because the zero term vanishes.','poisson-moments');
  add('poisson-mean-cancel',PM,'Cancel k against k! and pull out one λ','The remaining series starts with exponent zero.',R`E[X]=\lambda e^{-\lambda}\sum_{k=1}^{\infty}\frac{\lambda^{k-1}}{(k-1)!}`,'poisson',{stage:5,lambda:3,focus:'mean-cancel'},'Use k factorial equals k times k minus one factorial. Also write lambda to the k as lambda times lambda to the k minus one.','poisson-moments');
  add('poisson-mean-result',PM,'Reindex the series by j = k − 1','The sum becomes exp(λ) again.',R`E[X]=\lambda e^{-\lambda}\sum_{j=0}^{\infty}\frac{\lambda^j}{j!}=\lambda`,'poisson',{stage:6,lambda:3,focus:'mean-result'},'The change of index only renames the same sequence of terms. The exponential factors cancel, leaving lambda.','poisson-moments');
  add('poisson-factorial-moment',PM,'For variance, first average X(X − 1)','The k = 0 and k = 1 terms vanish.',R`E[X(X-1)]=\sum_{k=2}^{\infty}k(k-1)e^{-\lambda}\frac{\lambda^k}{k!}`,'poisson',{stage:7,lambda:3,focus:'factorial-moment'},'This is called a second factorial moment. Its form is useful because k times k minus one cancels the first two factors of k factorial.','poisson-moments');
  add('poisson-factorial-cancel',PM,'Cancel two factors and extract λ²','Shift the index by two.',R`E[X(X-1)]=\lambda^2e^{-\lambda}\sum_{j=0}^{\infty}\frac{\lambda^j}{j!}=\lambda^2`,'poisson',{stage:8,lambda:3,focus:'factorial-result'},'After cancellation the denominator is k minus two factorial. Put j equal to k minus two and recognize the exponential series.','poisson-moments');
  add('poisson-second-moment',PM,'Recover the ordinary second moment','Use X² = X(X − 1) + X.',R`E[X^2]=E[X(X-1)]+E[X]=\lambda^2+\lambda`,'poisson',{stage:9,lambda:3,focus:'second-moment'},'We have already computed both expectations on the right. Linearity applies even though these expressions involve the same random variable.','poisson-moments');
  add('poisson-moments',PM,'Subtract the square of the mean','Both the mean and variance equal λ.',R`E[X]=\lambda,\qquad\operatorname{Var}(X)=(\lambda^2+\lambda)-\lambda^2=\lambda`,'poisson',{stage:10,lambda:3,focus:'moments'},'Equal mean and variance is a property of this model. It does not mean every count model has that property. The standard deviation is the square root of lambda.','poisson-moments');

  const END = 'Use the model, then compare';
  add('poisson-rain',END,'What is the chance of exactly two drops?','Use one square foot for 0.01 seconds, so λ = 3.',R`P(X=\textcolor{#eab308}{2})=e^{-\textcolor{#38bdf8}{3}}\frac{\textcolor{#38bdf8}{3}^{\textcolor{#eab308}{2}}}{\textcolor{#eab308}{2!}}\approx\boxed{0.22404}`,'rain',{stage:4,rate:300,area:1,seconds:.01,lambda:3,k:2,focus:'exactly-two'},'Under the stated Poisson rainfall model, the chance is about 22.4 percent. Exactly two corresponds to the single bar at two, not a cumulative tail.','poisson-exposure');
  add('poisson-rain-moments',END,'Interpret the mean and variance for this window','An expected three drops does not guarantee three in every window.',R`E[X]=3,\qquad\operatorname{Var}(X)=3,\qquad\operatorname{SD}(X)=\sqrt3`,'rain',{stage:5,rate:300,area:1,seconds:.01,lambda:3,focus:'moments'},'Over repeated equal windows the average count approaches three. Individual counts vary according to the model.','poisson-moments');
  add('poisson-double-window',END,'Double only the observation time','The expected count doubles with exposure.',R`\lambda=300(1)(0.02)=6,\qquad E[X]=\operatorname{Var}(X)=6`,'rain',{stage:6,rate:300,area:1,seconds:.02,lambda:6,focus:'exposure'},'Hold the rate and area fixed, then double the time. Under a constant-rate model, lambda scales with the selected window.','poisson-exposure');
  add('poisson-detector',END,'The same exposure idea works for a detector','At three events per minute, a one-minute count has λ = 3.',R`\lambda=rt=3(1)=3`,'poisson',{stage:0,lambda:3,k:2,focus:'pmf'},'Assume constant rate and independent counts on disjoint intervals. Under this model the one-minute chance of exactly two events is the same 0.224042 calculated for the rain window.','poisson-exposure');
  add('poisson-detector-any',END,'Find the chance of at least one event','Only the zero-event probability is outside the event.',R`P(X\ge1)=1-e^{-3}\approx0.950213`,'poisson',{stage:1,lambda:3,k:0,focus:'zero'},'For a Poisson variable, P(X=0)=exp(-lambda). The complement is therefore particularly simple.','poisson-exposure');
  add('poisson-detector-half',END,'Now watch for thirty seconds','Convert the duration to one half minute first.',R`\lambda=3(0.5)=1.5`,'poisson',{stage:1,lambda:1.5,k:0,focus:'zero'},'The rate remains three events per minute, but the expected count for the shorter window is only 1.5.','poisson-exposure');
  add('poisson-detector-half-any',END,'Use the new mean for the new window','A shorter window makes at least one event less likely.',R`P(X\ge1)=1-e^{-1.5}\approx0.776870`,'poisson',{stage:1,lambda:1.5,k:0,focus:'zero'},'Always attach lambda to the selected exposure. For two minutes the mean would instead be six. For spatial counts the same principle gives lambda=rho times volume; the assumptions of homogeneous intensity and independent disjoint-region counts remain essential. Examples such as stars, price jumps, or idealized biological event sources suggest models but do not prove those assumptions.','poisson-exposure');

  const INS = 'Further review: infer a Poisson parameter';
  add('insurance-picture',INS,'Count insurance claims over one year','Assume a Poisson model with an unknown positive mean.',R`X\sim\operatorname{Poisson}(\lambda),\qquad\lambda>0`,'poisson',{stage:0,lambda:2,k:2,focus:'unknown',unknownParameter:true},'The parameter is not yet known to the solver. The following graph illustrates the eventual model; the unknown-parameter flag hides numerical bar heights until it has been found.','insurance-example');
  add('insurance-ratio',INS,'Translate the information about two counts','Two claims are three times as likely as four.',R`P(X=2)=3P(X=4)`,'poisson',{stage:0,lambda:2,k:2,focus:'ratio',unknownParameter:true},'Translate the sentence first. It does not say the count itself is three times larger. It compares two probabilities.','insurance-example');
  add('insurance-substitute',INS,'Insert the Poisson probabilities','Both sides contain the same exponential factor.',R`e^{-\lambda}\frac{\lambda^2}{2!}=3e^{-\lambda}\frac{\lambda^4}{4!}`,'poisson',{stage:0,lambda:2,k:2,focus:'ratio',unknownParameter:true},'The left side is the probability of two claims; the right side is three times the probability of four.','insurance-example');
  add('insurance-cancel',INS,'Cancel the common positive factors','Divide both sides by e⁻λ λ².',R`\frac1{2!}=\frac{3\lambda^2}{4!}`,'poisson',{stage:0,lambda:2,k:2,focus:'ratio',unknownParameter:true},'The cancellation is valid because lambda is positive. Simplify two factorial to two and four factorial to twenty-four.','insurance-example');
  add('insurance-parameter',INS,'Solve for the admissible parameter','Only the positive root can be the Poisson mean.',R`\lambda^2=4\quad\Longrightarrow\quad\lambda=2`,'poisson',{stage:0,lambda:2,k:2,focus:'parameter'},'The mean annual claim count is two under the stated model. We can now answer the requested tail question.','insurance-example');
  add('insurance-tail',INS,'Three or more claims means a tail','Its complement is zero, one, or two claims.',R`P(X\ge3)=1-P(X\le2)`,'poisson',{stage:0,lambda:2,k:3,focus:'tail',tailFrom:3},'The count is integer-valued. Keep the tail question separate from the earlier probability relation used to infer lambda.','insurance-example');
  add('insurance-tail-sum',INS,'Add the three probabilities in the complement','Substitute λ = 2 only after finding it.',R`P(X\ge3)=1-e^{-2}\left(1+2+\frac{2^2}{2!}\right)`,'poisson',{stage:0,lambda:2,k:3,focus:'tail',tailFrom:3},'The three terms in parentheses correspond to zero, one, and two claims.','insurance-example');
  add('insurance-result',INS,'Interpret the annual tail probability','About 32.3% of years have at least three claims under this model.',R`P(X\ge3)=1-5e^{-2}\approx0.323324`,'poisson',{stage:0,lambda:2,k:3,focus:'tail',tailFrom:3},'This is the final worked example from the canonical Chapter 5 notes. A fitted or inferred mean alone does not establish a Poisson model; the model was an assumption of the question.','insurance-example');

  add('review-bernoulli',END,'One trial: a Bernoulli record','A success is one; a failure is zero.',R`E[I]=p,\qquad\operatorname{Var}(I)=pq`,'summary',{stage:0,focus:'bernoulli'},'First recognize a single yes-or-no experiment. The variable records whether the outcome being counted occurred.','model-comparison');
  add('review-binomial',END,'Independent trials: a binomial count','Use fixed n and the same success probability p.',R`E[X]=np,\qquad\operatorname{Var}(X)=npq`,'summary',{stage:0,focus:'binomial'},'The count is the sum of independent Bernoulli variables. Linearity gives the mean; zero covariances give the variance.','model-comparison');
  add('review-hypergeometric',END,'Without replacement: a hypergeometric count','Use p = K/N for a sample from the finite population.',R`E[X]=np,\qquad\operatorname{Var}(X)=npq\frac{N-n}{N-1}`,'summary',{stage:0,focus:'hypergeometric'},'The Bernoulli variables have the same success probability on their own, but they are dependent. The dependence reduces the variance.','model-comparison');
  add('review-poisson',END,'Events in a fixed window: a Poisson count','Use λ for the expected count over that exposure.',R`E[X]=\lambda,\qquad\operatorname{Var}(X)=\lambda`,'summary',{stage:0,focus:'poisson'},'The homogeneous Poisson model assumes an appropriate constant rate and independent counts in disjoint exposure regions. Many rare independent opportunities motivate its binomial limit.','model-comparison');
  add('model-comparison',END,'Choose the model from the experiment','One trial; independent trials; a finite sample; or events in a window.','','summary',{stage:0,p:.2,n:12,N:250,K:50,lambda:3,focus:'models'},'For the hypergeometric row use p equal to K over N. First identify the experiment and assumptions, then select the formula. A count alone does not identify its distribution.','model-comparison');
  add('limits-comparison',END,'The two approximations change different things','Hypergeometric → binomial: enlarge the population. Binomial → Poisson: many rarer trials.',R`\begin{aligned}\text{Hypergeometric}\to\text{Binomial}:&\ n\text{ fixed},\ N\to\infty,\ K/N\to p\\\text{Binomial}\to\text{Poisson}:&\ n\to\infty,\ p\to0,\ np\to\lambda\end{aligned}`,'summary',{stage:1,p:.2,n:12,N:250,K:50,lambda:3,focus:'limits'},'Finish by asking what stays fixed in each approximation. The first keeps the number of draws fixed; the second keeps the expected count fixed while making the trials more numerous and individually rarer.','model-comparison');


  const coinSequenceIds = new Set(['count-five-trials','bernoulli-sum','binomial-fixed-trials','binomial-common-chance','binomial-independent-trials','binomial-assumptions']);
  for (const s of details) {
    if (coinSequenceIds.has(s.id) || /^count-reveal-/.test(s.id)) Object.assign(s.params,coin);
    else if (!s.params.experiment) Object.assign(s.params,{experiment:'generic',successLabel:'success',failureLabel:'failure',successSymbol:'S',failureSymbol:'F'});
    if (s.visual === 'cereal' || /^binomial-(bernoulli-sum|mean|variance-sum|moments)$/.test(s.id)) Object.assign(s.params,{experiment:'cereal',successLabel:'prize',failureLabel:'no prize',successSymbol:'1',failureSymbol:'0'});
    if (s.visual === 'urn' || s.visual === 'hypergeom') {
      const skittles = s.params.N === 250;
      Object.assign(s.params,{experiment:skittles?'skittles':'population',successLabel:skittles?'purple':'success',failureLabel:skittles?'not purple':'failure',successSymbol:'S',failureSymbol:'F'});
    }
    if (/^(hypergeometric-bernoullis|marginal-|variance-)/.test(s.id) && s.visual === 'sequence') s.params.experiment='population';
  }

  const byId = Object.fromEntries(details.map(s => [s.id,s]));
  const take = (id, override = {}) => ({...byId[id],...override,params:{...byId[id].params,...override.params}});
  // The complete review begins with one trial. Wednesday can resume at cereal-rule;
  // the main live sequence after that anchor follows Wednesday-50-Minute-Plan.md.
  // Further-review states follow the live recap so they never interrupt its pacing.
  const classroom = [
    take('bernoulli-trial'),
    take('bernoulli-labels'),
    take('bernoulli-outcomes'),
    take('bernoulli-failure-chance'),
    take('bernoulli-variable'),
    take('bernoulli-name'),
    take('bernoulli-die-outcomes'),
    take('bernoulli-die-success'),
    take('bernoulli-die-probability'),
    take('bernoulli-die-variable'),
    take('bernoulli-mean'),
    take('bernoulli-variance',{title:'A Bernoulli trial has variance pq',body:'Variation disappears when an outcome is certain.',eq:R`\operatorname{Var}(I)=\textcolor{#eab308}{p}\textcolor{#38bdf8}{q}`}),
    take('count-five-trials'),
    ...Array.from({length:5},(_,i)=>take(`count-reveal-${i+1}`)),
    take('bernoulli-sum'),
    take('binomial-fixed-trials'),
    take('binomial-common-chance'),
    take('binomial-independent-trials'),
    take('binomial-assumptions'),
    take('binomial-general-p'),
    take('sequence-success-factors'),
    take('sequence-failure-factors'),
    take('count-event'),
    ...Array.from({length:9},(_,i)=>take(`count-arrangement-${i+2}`)),
    take('count-general',{body:'The binomial coefficient counts these choices of success positions.'}),
    take('binomial-one-term'),
    take('binomial-example'),
    take('binomial-support'),
    take('cereal-boxes'),
    take('cereal-claim'),
    take('cereal-expected15'),
    take('cereal-rule'),
    take('cereal-rule-sample'),
    take('cereal-false-reject',{body:'At p = 0.15 the claim is true; these low counts reject it anyway.'}),
    take('cereal-rate-reference'),
    take('cereal-truth-changes'),
    take('cereal-error-event'),
    take('cereal-complement'),
    take('cereal-miss-sum'),
    take('cereal-miss'),
    take('cereal-miss-boxes'),
    take('cereal-two-errors'),
    take('binomial-bernoulli-sum',{body:'Each indicator is a Bernoulli variable: one for a prize, zero otherwise.'}),
    take('binomial-mean',{eq:R`E[X]=\underbrace{p+\cdots+p}_{n\text{ trials}}=np`}),
    take('binomial-variance-sum',{eq:R`\operatorname{Var}(X)=\underbrace{pq+\cdots+pq}_{n\text{ independent trials}}=npq`}),
    take('binomial-moments',{body:'Expectations add without independence; this variance formula uses independent trials.'}),
    take('theorem-factors',{section:'Why the binomial probabilities sum to one'}),
    take('theorem-like-terms',{section:'Why the binomial probabilities sum to one'}),
    take('binomial-theorem',{section:'Why the binomial probabilities sum to one',visual:'binomial',params:{n:5,p:.3,stage:2,focus:'total'},body:'Choose which k factors supply p; the other factors supply q.'}),
    take('binomial-normalization',{section:'Why the binomial probabilities sum to one'}),
    take('fair-sequence-probability',{section:'Fair trials become a counting problem',params:{n:4,k:2,p:.5}}),
    take('binomial-fair',{section:'Fair trials become a counting problem',params:{n:4,k:2,p:.5,stage:4,focus:'fair'}}),
    take('fair-count-total',{section:'Fair trials become a counting problem',title:'Four fair flips: exactly two successes',visual:'combinations',params:{n:4,k:2,p:.5,stage:4,focus:'fair'},body:'Six favorable sequences out of sixteen equally likely sequences.',eq:R`P(X=2)=\frac{\binom42}{2^4}=\frac6{16}=\frac38`,notes:'Choose two of four success positions. There are six such sequences. Each of all sixteen length-four binary sequences has probability one sixteenth.'}),
    take('replacement-return'),
    take('replacement-binomial'),
    take('without-remove'),
    take('without-failure'),
    take('skittles-population'),
    take('skittles-sample'),
    take('hypergeometric-denominator'),
    take('hypergeometric-success-count'),
    take('hypergeometric-failure-count'),
    take('hypergeometric-product'),
    take('hypergeometric-skittles'),
    take('hypergeometric-pmf'),
    take('marginal-shuffle',{title:'Imagine the Skittles shuffled into a row',body:'Before revealing any draw, all positions are treated alike.',eq:'',params:{experiment:'skittles',successLabel:'purple',failureLabel:'not purple',n:12,k:2,p:.2,populationN:250,populationK:50,concealed:true,dependent:true,focus:'shuffle'},notes:'Uniform sampling without replacement is equivalent to shuffling all 250 distinct Skittles and revealing the first twelve positions. The diagram shows twelve covered positions of that longer row.'}),
    take('marginal-position',{body:'Any fixed position is equally likely to hold any of the 250 Skittles.',eq:R`P(\text{purple at position }i)=\frac{50}{250}=0.2`,params:{experiment:'skittles',successLabel:'purple',failureLabel:'not purple',n:12,k:2,p:.2,populationN:250,populationK:50,concealed:true,dependent:true,highlight:[4]},notes:'There are fifty purple objects among the two hundred fifty that could occupy position five. This chance describes the position on its own, before other outcomes are known. This is sometimes called a marginal probability.'}),
    take('hypergeometric-mean',{body:'Each draw is a Bernoulli variable with mean p = K/N.',eq:R`E[X]=np`,notes:'Indicators are simply zero-or-one Bernoulli variables. Expectations add even though these draws are dependent.'}),
    take('hypergeometric-mean-skittles'),
    take('marginal-given-success',{title:'A known purple draw changes the next chance',body:'One purple has been removed from the remaining population.',eq:R`P(S_2\mid S_1)=\frac{49}{249}\ne\frac{50}{250}`,params:{experiment:'skittles',successLabel:'purple',failureLabel:'not purple',N:250,K:50,n:12,k:6,p:.2},notes:'Equal chances before learning other outcomes do not mean independence. A known purple first draw reduces the purple share in the remaining population.'}),
    take('hypergeometric-variance',{body:'Dependence changes the variance through this finite-population correction.',eq:R`\operatorname{Var}(X)=\textcolor{#eab308}{n}\textcolor{#a855f7}{p}\textcolor{#14b8a6}{q}\,\frac{N-\textcolor{#eab308}{n}}{N-1}`,notes:'For N greater than one, the formula accounts for negative dependence. The detailed route derives the covariance. The mean remains np because linearity does not require independence.'}),
    take('hypergeometric-variance-skittles'),
    take('hypergeometric-full-sample'),
    take('poisson-tiny-opportunities',{title:'Imagine many rare opportunities',body:'λ is the expected total count from many independent opportunities, each with a tiny event chance.'}),
    take('poissonlimit-compare',{id:'poissonlimit-small',title:'Start with ten independent opportunities',body:'Ten trials with success chance 0.3 give an expected count of three.',eq:R`n=10,\qquad p=0.3,\qquad np=3`,params:{n:10,p:.3,lambda:3,focus:'moments'},notes:'The purple bars give exact binomial probabilities. The blue reference marks give Poisson probabilities with the same expected count, lambda three.'}),
    take('poissonlimit-compare',{id:'poissonlimit-medium',title:'Make the opportunities more numerous and rarer',body:'Fifty trials with success chance 0.06 still give an expected count of three.',eq:R`n=50,\qquad p=0.06,\qquad np=3`,params:{n:50,p:.06,lambda:3,focus:'moments'},notes:'Increasing the number of opportunities while reducing their individual success chance preserves np. Watch the exact binomial bars approach the Poisson reference marks.'}),
    take('poissonlimit-compare',{body:'Increase n and decrease p while keeping np near λ.',eq:R`\operatorname{Bin}(n,p)\approx\operatorname{Poisson}(\lambda),\qquad\lambda=np`,notes:'Use this shape comparison briefly. With expected count three, n=10,50,500 use p=0.3,0.06,0.006. The full limit proof belongs to the detailed route.'}),
    take('poisson-rain-picture',{eq:R`X=\text{number of drops in the window}`}),
    take('poisson-assumptions',{body:'Assume a constant rate and independent counts in disjoint windows.',eq:''}),
    take('poisson-rate'),
    take('poisson-exposure-window'),
    take('poisson-rate-units'),
    take('poisson-pmf'),
    take('poisson-rain'),
    take('poisson-moments',{title:'Poisson mean and variance both equal λ',body:'Both quantities equal the expected count for this window.',eq:R`E[X]=\lambda,\qquad\operatorname{Var}(X)=\lambda`,notes:'For the rain window both equal three. Do not expand the infinite series in this live route; those proofs remain in the detailed route.'}),
    take('review-bernoulli'),
    take('review-binomial'),
    take('review-hypergeometric'),
    take('review-poisson'),
    take('model-comparison'),
    take('poisson-double-window'),
    // Optional review continues after the Wednesday finishing point.
    take('independence-picture',{section:'Further review: independence and variance'}),
    take('independence-learn-first',{section:'Further review: independence and variance'}),
    take('independence-joint',{section:'Further review: independence and variance'}),
    take('linearity-general',{section:'Further review: independence and variance'}),
    take('product-result',{section:'Further review: independence and variance'}),
    take('covariance-center',{section:'Further review: independence and variance'}),
    take('covariance-definition',{section:'Further review: independence and variance'}),
    take('covariance-compute',{section:'Further review: independence and variance'}),
    take('variance-general-sum',{section:'Further review: independence and variance'}),
    take('variance-difference',{section:'Further review: independence and variance'}),
    take('zero-covariance-picture',{section:'Further review: independence and variance'}),
    take('zero-covariance-means',{section:'Further review: independence and variance'}),
    take('zero-covariance-product',{section:'Further review: independence and variance',eq:R`\operatorname{Cov}(X,Y)=0`}),
    take('zero-covariance-dependent',{section:'Further review: independence and variance'}),
    take('independent-copies',{section:'Further review: independence and variance'}),
    take('same-variable-twice',{section:'Further review: independence and variance'}),
    take('hyperlimit-small',{section:'Further review: how the counting models connect'}),
    take('hyperlimit-large',{section:'Further review: how the counting models connect',body:'A fixed sample barely depletes a sufficiently large population.',eq:R`\frac{N-n}{N-1}\approx1`,notes:'Hold sample size ten fixed and increase population size. The formal finite-product proof stays in the detailed route.'}),
    take('poisson-lab-exact',{section:'Further review: how the counting models connect',body:'X counts errors among 1000 independent specimens; each has error probability p = 0.002.'}),
    take('poisson-lab-fixed-mean',{section:'Further review: how the counting models connect'}),
    take('insurance-picture'),
    take('insurance-ratio'),
    take('insurance-substitute'),
    take('insurance-parameter'),
    take('insurance-tail'),
    take('insurance-tail-sum'),
    take('insurance-result')
  ];
  // A beat is one meaningful action followed by an indefinite reading pause.
  // Its frames are internal animation states, not extra clicks. Keep every raw
  // semantic id addressable for notes/quiz links and detailed inspection.
  const detailedBeatEnds = [
    ['bernoulli-failure-chance','A fair coin supplies two outcomes'],
    ['bernoulli-name','Turn heads or tails into a Bernoulli record'],
    ['bernoulli-die-variable','A six-outcome experiment can make a Bernoulli record'],
    ['bernoulli-variance','Find the Bernoulli mean and variance'],
    ['bernoulli-deviations-factor','Check the variance from squared deviations'],
    ['bernoulli-endpoints','Compare uncertainty with certainty'],
    ['bernoulli-sum','Five coin flips become one count',750],
    ['binomial-assumptions','Specify the binomial experiment'],
    ['sequence-rearrange','One sequence: multiply its success and failure chances'],
    ['count-arrangement-10','Find all ten arrangements',650],
    ['count-general','Count positions without counting their order twice'],
    ['binomial-support','Turn arrangement counts into a probability model'],
    ['pascal-build-1-1','Start Pascal’s triangle',1100],
    ['pascal-build-2-2','Build Pascal row two',1100],
    ['pascal-build-3-3','Build Pascal row three',1100],
    ['pascal-build-4-4','Build Pascal row four',1100],
    ['pascal-build-5-5','Build Pascal row five',1100],
    ['pascal-include','Explain the two parent entries'],
    ['pascal-five','Add the two cases and read the completed row'],
    ['binomial-theorem','A product expansion counts the same arrangements'],
    ['binomial-normalization','The binomial probabilities sum to one'],
    ['fair-count-total','Fair trials turn probability into counting'],
    ['cereal-claim','Set up the cereal-box claim'],
    ['cereal-expected15','Add fifty prize chances to find the expected count'],
    ['cereal-rule-sample','Compare a low count with the expected count'],
    ['cereal-false-reject','Use the decision rule when the claim is true'],
    ['cereal-truth-changes','Change the true rate; keep the cutoff fixed'],
    ['cereal-error-event','Identify the counts that miss the false claim'],
    ['cereal-miss','Compute the chance of missing the false claim'],
    ['cereal-miss-boxes','Interpret the answer in the fifty boxes'],
    ['cereal-mean-cutoff','Distinguish two errors and a decision cutoff'],
    ['cereal-cutoff-miss','Changing the cutoff trades one error for the other'],
    ['binomial-mean','Add the Bernoulli averages'],
    ['binomial-cereal-moments','Use independence to add the variances'],
    ['independence-learn-first','Learning one independent outcome leaves the other unchanged'],
    ['independence-conditional','Connect joint and conditional independence'],
    ['linearity-general','Linearity works with dependent variables too'],
    ['product-result','Independence separates an expected product'],
    ['covariance-compute','Covariance averages paired deviations'],
    ['variance-general-sum','The variance of a sum includes two cross terms'],
    ['variance-difference','See what independence and subtraction change'],
    ['zero-covariance-dependent','A zero covariance can conceal dependence'],
    ['symmetric-dependent','Symmetric zero means do not imply independence'],
    ['many-variable-variance','Every distinct pair supplies a covariance'],
    ['same-variable-twice','Distinguish two independent copies from twice one variable'],
    ['replacement-binomial','Replacement restores the success chance'],
    ['without-new-count','Leaving an object out changes later chances'],
    ['skittles-sample','Skittles: define success, population, and sample'],
    ['hypergeometric-product','Count all samples, then the favorable samples'],
    ['hypergeometric-normalization','The hypergeometric formula counts every possible sample'],
    ['hypergeometric-skittles','Evaluate the chance of six purple Skittles'],
    ['marginal-position','A shuffled row treats every position equally'],
    ['marginal-given-failure','Conditioning changes the next-draw chance'],
    ['marginal-lotp','Combine the two routes with total probability'],
    ['hypergeometric-mean-skittles','Equal individual chances give the mean np'],
    ['variance-covariance','Find the covariance of two draw records'],
    ['variance-pq','Simplify the negative covariance'],
    ['hypergeometric-variance-skittles','Combine every pair into the variance correction'],
    ['balanced-population-dependent','Check the finite-population correction'],
    ['hyperlimit-large','A fixed sample depletes a larger population less'],
    ['hyperlimit-statement','Compare simulation and the limiting model'],
    ['hyperlimit-scale-factors','Rewrite sampling probabilities as finite products'],
    ['hyperlimit-pmf-proof','Take the finite products to their binomial limit'],
    ['poisson-lab-zero','Many rare errors form a binomial count'],
    ['poisson-lab-fixed-mean','Connect rare-event probabilities to their mean count'],
    ['poisson-lambda','Connect a rain count to many tiny opportunities'],
    ['poisson-rate-units','Convert the rain rate and exposure into lambda'],
    ['poisson-support','Introduce the Poisson probability model'],
    ['poissonlimit-expand-count','Insert p = lambda / n into the binomial pmf'],
    ['poissonlimit-count-result','Take the success-count factor to its limit'],
    ['poissonlimit-result','The no-event factor supplies the exponential'],
    ['poisson-source-comparison','Compare exact counts, simulated counts, and the limit'],
    ['poisson-normalization','Check that Poisson probabilities sum to one'],
    ['poisson-mean-result','Shift the series to find the Poisson mean'],
    ['poisson-moments','Use the factorial moment to find the variance'],
    ['poisson-double-window','Apply the rain model and change the exposure'],
    ['poisson-detector-any','Use a complement to count detector events'],
    ['poisson-detector-half-any','Change the duration, then change lambda'],
    ['insurance-ratio','Translate a relation between two claim probabilities'],
    ['insurance-parameter','Cancel common factors and infer lambda'],
    ['insurance-result','Use the inferred parameter to find a tail probability'],
    ['review-poisson','Match each experiment to its count model'],
    ['limits-comparison','Compare the models and the two different limits']
  ];
  const classroomBeatEnds = [
    ['bernoulli-failure-chance','A fair coin supplies two outcomes'],
    ['bernoulli-name','Turn heads or tails into a Bernoulli record'],
    ['bernoulli-die-variable','Choose a die event and record whether it occurs'],
    ['bernoulli-variance','Keep the Bernoulli mean and variance'],
    ['bernoulli-sum','Five coin flips become one count',750],
    ['binomial-assumptions','Specify the binomial experiment'],
    ['sequence-failure-factors','One sequence: multiply its success and failure chances'],
    ['count-arrangement-10','Find all ten arrangements',650],
    ['binomial-one-term','Multiply arrangements by the probability of one'],
    ['binomial-support','Use the formula for every possible count'],
    ['cereal-claim','Set up the cereal-box claim'],
    ['cereal-expected15','Add fifty prize chances to find the expected count'],
    ['cereal-rule-sample','Compare a low count with the expected count'],
    ['cereal-false-reject','Recall the rule and the first error'],
    ['cereal-truth-changes','Change the true rate; keep the cutoff fixed'],
    ['cereal-error-event','Identify the counts that miss the false claim'],
    ['cereal-miss','Compute the chance of missing the false claim'],
    ['cereal-miss-boxes','Interpret the answer in the fifty boxes'],
    ['cereal-two-errors','Compare the two different errors'],
    ['binomial-moments','Recall why the binomial mean and variance differ'],
    ['binomial-normalization','The binomial theorem makes the probabilities sum to one'],
    ['fair-count-total','Four fair flips: count six favorable sequences'],
    ['replacement-binomial','Replacement restores the success chance'],
    ['without-failure','Without replacement, earlier draws matter'],
    ['skittles-sample','Skittles: define success, population, and sample'],
    ['hypergeometric-product','Count all samples, then the favorable samples'],
    ['hypergeometric-pmf','Calculate the Skittles chance and read the general rule'],
    ['marginal-position','A shuffled row treats every position equally'],
    ['hypergeometric-mean-skittles','Equal individual chances still give the mean np'],
    ['hypergeometric-full-sample','Dependence reduces the variance'],
    ['poissonlimit-compare','Many rarer trials approach a Poisson count'],
    ['poisson-assumptions','Specify the rain count and its model assumptions'],
    ['poisson-rate-units','Rate times exposure gives the expected count'],
    ['poisson-moments','Find the two-drop probability and the Poisson moments'],
    ['review-poisson','Match each experiment to its count model'],
    ['poisson-double-window','Recap, then double the observation window'],
    ['independence-joint','Review what independence says'],
    ['product-result','Distinguish the sum and product expectation rules'],
    ['covariance-compute','Covariance measures paired departures'],
    ['variance-difference','Include the covariance when adding or subtracting'],
    ['zero-covariance-dependent','Zero covariance does not imply independence'],
    ['same-variable-twice','Distinguish independent copies from a doubled variable'],
    ['hyperlimit-large','A large population approaches replacement'],
    ['poisson-lab-fixed-mean','Recognize a rare-event binomial model'],
    ['insurance-ratio','Translate the insurance probability relation'],
    ['insurance-parameter','Find the unknown Poisson mean'],
    ['insurance-result','Use that mean to find a tail probability']
  ];
  const makeBeats = (states, ends) => {
    let cursor=0;
    const beats=ends.map(([end,title,pace])=>{
      const stop=states.findIndex((state,index)=>index>=cursor && state.id===end);
      if(stop<cursor) throw new Error(`Missing conceptual-beat endpoint: ${end}`);
      const group=states.slice(cursor,stop+1); cursor=stop+1;
      let intervals=group.map((state,index)=>index===group.length-1?0:pace??(state.eq.length>140?2400:2100));
      // Short automatic demonstrations end in a presenter/student-controlled pause.
      const duration=intervals.reduce((sum,n)=>sum+n,0);
      if(duration>7800) intervals=intervals.map(n=>Math.round(n*7800/duration));
      return {id:group[0].id,title,section:group[0].section,frames:group.map(state=>state.id),intervals};
    });
    if(cursor!==states.length) throw new Error(`Unassigned animation states after ${states[cursor].id}`);
    return beats;
  };
  const beats={details:makeBeats(details,detailedBeatEnds),classroom:makeBeats(classroom,classroomBeatEnds)};
  // Hold one sentence during a demonstration; its individual frame explanations
  // remain available in the notes panel without competing for visual attention.
  const beatCaptions={
    'bernoulli-failure-chance':'A fair coin gives heads or tails; choose heads as success and tails as failure.',
    'bernoulli-name':'Record success as 1 and failure as 0: this Bernoulli variable is also called an indicator.',
    'bernoulli-die-variable':'The die has six outcomes, but recording whether it lands on 5 or 6 gives only two values: 1 or 0.',
    'bernoulli-variance':'For a Bernoulli variable, the mean is p and the variance is p(1 − p).',
    'bernoulli-deviations-factor':'Weight each squared distance from the mean by its probability, then simplify.',
    'bernoulli-endpoints':'A Bernoulli variable has the greatest spread at p = 1/2 and no spread when the outcome is certain.',
    'bernoulli-sum':'Each coin flip supplies a Bernoulli record; adding the five records counts the heads.',
    'binomial-assumptions':'A binomial count uses a fixed number of independent trials with the same success probability p.',
    'sequence-rearrange':'Two successes and three failures have probability p²q³ in any one specified arrangement.',
    'sequence-failure-factors':'Multiply a factor p for each success and a factor q for each failure in the specified sequence.',
    'count-arrangement-10':'Keep exactly two successes and move their positions to find all ten different arrangements.',
    'count-general':'Choose the success positions; choosing those positions in a different order does not make a new arrangement.',
    'binomial-one-term':'Add equal probabilities by multiplying the number of arrangements by the probability of one arrangement.',
    'binomial-support':'The binomial pmf assigns a probability to each possible success count from 0 through n.',
    'pascal-build-1-1':'The boundary entries are 1; every interior entry is the sum of the two entries immediately above it.',
    'pascal-build-2-2':'The boundary entries are 1; every interior entry is the sum of the two entries immediately above it.',
    'pascal-build-3-3':'The boundary entries are 1; every interior entry is the sum of the two entries immediately above it.',
    'pascal-build-4-4':'The boundary entries are 1; every interior entry is the sum of the two entries immediately above it.',
    'pascal-build-5-5':'The boundary entries are 1; every interior entry is the sum of the two entries immediately above it.',
    'pascal-include':'Split the choices into two cases: the new position is either excluded or included.',
    'pascal-five':'Add the two disjoint cases; each entry counts arrangements with that many successes.',
    'binomial-theorem':'Choosing p or q from each factor produces the same arrangements counted by the binomial coefficients.',
    'binomial-normalization':'The binomial theorem adds all the probabilities into (p + q)ⁿ, which equals 1 because p + q = 1.',
    'fair-count-total':'With p = 1/2, all binary sequences are equally likely: divide favorable sequences by all sequences.',
    'cereal-claim':'Count prize-containing boxes in a sample of 50 to assess the claim that at least 15% contain a prize.',
    'cereal-expected15':'Each of the 50 boxes contributes 0.15 to the expected count: repeated samples average 7.5 prizes.',
    'cereal-rule-sample':'Four is below the expected 7.5 prizes, motivating a low-count rejection rule; the stated cutoff remains a separate choice.',
    'cereal-truth-changes':'Changing the true rate from 15% to 5% moves the expected count from 7.5 to 2.5, while the cutoff stays at 4.',
    'cereal-miss-boxes':'At p = 0.05, getting 5 or more prizes leads the rule to miss the false claim; these outcomes have total probability 10.36%.',
    'cereal-false-reject':'Reject the claim when X ≤ 4; at p = 0.15, this region represents rejecting a true claim.',
    'cereal-error-event':'At a true prize rate of 5%, the unchanged rule misses the false claim when X ≥ 5.',
    'cereal-miss':'At p = 0.05, subtract the probability of 0 through 4 prizes from 1 to find the missed-claim probability.',
    'cereal-two-errors':'The two errors use different true prize rates, so their probabilities are not complements of one another.',
    'cereal-mean-cutoff':'The mean describes the count distribution; the decision cutoff is a separate choice that determines the error region.',
    'cereal-cutoff-miss':'Lowering the rejection cutoff reduces false rejections but increases the chance of missing a false claim.',
    'binomial-mean':'Add the means of the Bernoulli prize records: linearity gives np without requiring independence.',
    'binomial-cereal-moments':'Independence lets the Bernoulli variances add, giving npq for the binomial count.',
    'binomial-moments':'The Bernoulli prize records give mean np by linearity and variance npq using independence.',
    'independence-learn-first':'For independent trials, learning the first outcome leaves the probabilities of the second outcome unchanged.',
    'independence-joint':'Independence means learning one outcome does not change the other, and joint probabilities factor.',
    'independence-conditional':'Joint probabilities factor, and conditional probabilities stay unchanged when the conditioning event has positive probability.',
    'linearity-general':'Expectations add even when the variables are dependent.',
    'product-result':'Independence lets an expected product separate into the product of the two expectations.',
    'covariance-compute':'Center both variables at their means, multiply the paired deviations, and average those products.',
    'variance-general-sum':'Squaring the sum of centered deviations produces two individual squares and two covariance cross terms.',
    'variance-difference':'The individual variances add; the covariance term depends on whether the variables are added or subtracted.',
    'zero-covariance-dependent':'For X equally likely −1, 0, or 1 and Y = X², covariance is zero even though knowing X determines Y.',
    'symmetric-dependent':'If B = A and A is equally likely −1 or 1, both means are zero but the variables are fully dependent.',
    'many-variable-variance':'The variance of a sum includes every individual variance and twice the covariance of each distinct pair.',
    'same-variable-twice':'Independent copies can differ; doubling one variable doubles every deviation and multiplies its variance by four.',
    'replacement-binomial':'Replacing each drawn object restores the population composition and keeps each success chance at K/N.',
    'without-new-count':'Without replacement, each draw changes the population composition, so later chances depend on earlier outcomes.',
    'without-failure':'Without replacement, the remaining success chance changes according to the outcome of the previous draw.',
    'skittles-sample':'Purple means success here: sample 12 from 250 Skittles containing 50 purple and ask for exactly 6 purple.',
    'hypergeometric-product':'Choose six purple and six nonpurple candies; compare these samples with all samples of twelve.',
    'hypergeometric-normalization':'Each sample has exactly one success count; partitioning all samples by that count makes the probabilities sum to 1.',
    'hypergeometric-skittles':'Divide favorable samples by all possible samples to obtain about a 1.376% chance of exactly 6 purple.',
    'hypergeometric-pmf':'Choosing the successes and failures separately gives the hypergeometric pmf and the Skittles probability.',
    'marginal-position':'Imagine shuffling every labeled object: each position has the same chance of containing any particular object.',
    'marginal-given-failure':'Knowing the first outcome changes the second chance: a success leaves 3/9, while a failure leaves 4/9.',
    'marginal-lotp':'Weight both conditional routes by their first-draw chances; total probability returns the second-draw chance to 4/10.',
    'hypergeometric-mean-skittles':'Before conditioning on other draws, each Bernoulli record has success chance K/N; adding these means gives np.',
    'variance-covariance':'Two successes without replacement are less likely than independent successes, producing a negative covariance.',
    'variance-pq':'Simplify the paired-success covariance to −pq/(N − 1), showing exactly how the dependence enters.',
    'hypergeometric-variance-skittles':'Add the individual Bernoulli variances and all pair covariances to obtain the finite-population correction.',
    'hypergeometric-full-sample':'Dependence reduces variance by the factor (N − n)/(N − 1); sampling the whole population makes the count certain.',
    'balanced-population-dependent':'The correction gives zero variance for a full sample and applies even when half the population are successes.',
    'hyperlimit-large':'Hold the sample size and success fraction fixed: removing the sample matters less as the population grows.',
    'hyperlimit-statement':'Simulation fluctuates around the exact law; with fixed sample size, the hypergeometric law approaches the binomial law.',
    'hyperlimit-scale-factors':'Write the sampling probabilities as finite products and divide each population factor by N.',
    'hyperlimit-pmf-proof':'Each fixed success factor approaches p and each failure factor approaches q, leaving the binomial pmf.',
    'poisson-lab-zero':'A thousand independent specimens with a small error chance give a binomial error count.',
    'poisson-lab-fixed-mean':'More specimens with a smaller error chance can keep the same expected error count.',
    'poisson-lambda':'Count events in a fixed window and imagine many tiny opportunities, each with a small event chance.',
    'poisson-assumptions':'For rain, fix the area and time and assume a constant rate with independent counts in disjoint windows.',
    'poisson-rate-units':'Multiply 300 drops per square foot per second by 1 square foot and 0.01 seconds to get λ = 3 expected drops.',
    'poisson-support':'A Poisson variable counts events: possible values are 0, 1, 2, … and λ is the expected count.',
    'poissonlimit-expand-count':'Set p = λ/n in the binomial pmf, then separate the counting factors from the no-event factors.',
    'poissonlimit-count-result':'With k fixed, the success and arrangement factors approach λᵏ/k! as n grows.',
    'poissonlimit-result':'The no-event factor approaches e⁻λ; combine it with λᵏ/k! to obtain the Poisson pmf.',
    'poissonlimit-compare':'Increase n and decrease p while keeping np near λ; the binomial count approaches a Poisson count.',
    'poisson-source-comparison':'Compare the exact distributions and sampled counts as many independent opportunities become rarer.',
    'poisson-normalization':'Factor out e⁻λ and recognize the exponential series; the remaining factors multiply to 1.',
    'poisson-mean-result':'Cancel k against k!, shift the sum, and recognize the exponential series to obtain mean λ.',
    'poisson-moments':'First find E[X(X − 1)], then recover E[X²] and subtract the squared mean to obtain variance λ.',
    'poisson-double-window':'With the rate and area fixed, doubling the observation time doubles λ and therefore the expected count.',
    'poisson-detector-any':'For at least one detector event, subtract the zero-event probability from 1.',
    'poisson-detector-half-any':'Halving the observation time halves λ; use this new mean when computing the chance of an event.',
    'insurance-ratio':'Translate “two claims are three times as likely as four” into an equation using the Poisson pmf.',
    'insurance-parameter':'Cancel the common exponential factor and solve for the positive Poisson mean.',
    'insurance-result':'With λ = 2, subtract the probabilities of 0, 1, and 2 claims from 1 to find the probability of at least 3.',
    'review-poisson':'Match the experiment to its assumptions: one trial, independent repeated trials, sampling without replacement, or events in a window.',
    'limits-comparison':'A growing population gives the hypergeometric-to-binomial limit; many rarer trials give the binomial-to-Poisson limit.'
  };
  for(const [mode,sequence] of Object.entries(beats))for(const beat of sequence){
    const end=beat.frames.at(-1),states=mode==='classroom'?classroom:details;
    beat.caption=beatCaptions[end]??states.find(state=>state.id===beat.frames[0]).body;
    if(mode==='classroom'&&end==='poisson-moments')beat.caption='Use λ = 3 to find the probability of exactly two drops; for a Poisson count, both mean and variance equal λ.';
  }
  window.LESSON = {title:'Counting models: Bernoulli → Binomial → Hypergeometric → Poisson',details,classroom,beats};
})();
