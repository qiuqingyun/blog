---
title: 论安全计算的部署：具有Cardinality的隐私集合交点求和问题
---

## 摘要

在这项工作中，我们讨论了我们在行业内部署加密安全计算协议的成功努力。我们考虑的问题是隐私计算广告活动的总转换率。这个基础功能可以被抽象为具有Cardinality的私人交叉和（PI-Sum）。在这种情况下，两方持有包含用户标识符的数据集，其中一方还拥有与其每个用户标识符相关的整数值。双方希望了解他们共同拥有的标识符的数量以及与这些用户相关的整数值的总和，而不透露任何有关他们私人输入的信息。

我们确定了主要的特性和有利因素，这些特性和因素使得部署一个加密协议成为可能、实用，并被独特地定位为手头任务的一个解决方案。我们描述了我们的部署环境和最相关的效率衡量标准，在我们的环境中，它是通信开销而不是计算。我们还提出了一个货币成本模型，可以作为一个统一的成本衡量标准，以及反映我们使用情况的计算模型：一个低优先级的批量计算。

我们提出了三个带cardinality的PI-Sum协议：我们目前部署的协议，它依赖于Diffie-Hellman风格的双重掩码，以及两个新的协议，它们利用了最近的私有集相交（PSI）技术，使用不经意传输和加密的Bloom过滤器。当用不同的加法同态加密方案进行实例化时，我们将后面两个协议与我们的原始解决方案进行比较。我们实现了我们的构造并比较了它们的成本。我们还与最近用于计算两个数据集的交集的通用方法进行了比较，结果表明，我们最好的协议的货币成本比已知的最佳通用方法低20倍。

<!--more-->

## 1 介绍

安全的多方计算(MPC)长期以来一直致力于实现对来自多个来源的数据的联合分析，同时保持每个输入源的隐私。在过去的十年中，该领域的最新发展显示了令人印象深刻的效率改进，表明这一承诺超越了可行性的结果，进入了实际的实施。然而，这种技术在实际工业环境中的应用却非常有限。
在本文中，我们介绍了我们在一个特定的商业应用中使用加密MPC技术的工作：归属总的广告转换。我们的解决方案已经在实践中使用了几年，在本文中我们讨论了我们在这个问题上部署和使用MPC解决方案所遇到的各种限制，以及这些限制如何影响我们选择实施的加密协议。我们的应用问题与私有集交集（PSI）问题有相似之处，但我们需要的确切功能是PSI问题的扩展，我们称之为有心性的私有集交集和。然而，由于PSI的技术水平已经有了巨大的进步[11]、[31]、[37]、[47]、[49]、[51]、[55]，通常以我们的商业场景作为实际应用的例子，在这项工作中，我们考虑最近有效的PSI构建方法以及如何将它们扩展到我们设置的解决方案。在低优先级的 "批量计算 "环境中执行时，我们将这些构造的效率成本与我们原来的解决方案的效率成本进行比较，因为在这种环境中不需要实时得到结果。我们通过使用云供应商对计算和网络资源收取的价格来模拟货币成本，我们发现这是对我们部署环境中的成本的良好近似。这种约束与安全计算领域的大多数工作所考虑的约束不同，这些工作通常侧重于最小化端到端的运行时间。

**广告转换**：当用户在某个网站上看到某个公司的在线广告，然后在该公司的商店里进行购买时，就会发生广告转换。投放广告的公司想知道它有多少收入可以归功于其在线广告活动。然而，计算这些归因统计所需的数据是由两方分担的：广告供应商和公司，前者知道哪些用户看过某个特定的广告，后者知道谁购买了产品以及他们花了多少钱。这两方可能不愿意或无法公开基础数据，但双方仍希望计算出一个总体的人口水平测量：有多少用户看到了广告并进行了相应的购买，以及这些用户总共花费了多少钱。他们希望在做到这一点的同时，确保在输入的数据集中，除了这些总量值之外，没有任何关于个人用户的信息被披露。

**具有Cardinality的隐私集合交点求和**：抽象地讲，上述问题可以被看作是私有集交集问题的一个变种，我们称之为具有Cardinality的隐私集合交点求和问题。在这种情况下，有两方拥有由标识符组成的私有输入集，其中一方还拥有与每个标识符相关的整数值。双方希望了解两个输入集的交集中所有标识符的相关整数值的总和，以及交集的cardinality（或大小），但除此之外就没有了。特别是，任何一方都不应该了解交集中的实际标识符，也不应该了解关于另一方数据的任何额外信息（除了他们的输入集的大小），例如比交集上的总数更细的相关值。此外，双方可以选择以交集的最小阈值大小为条件来揭示交集的总和。

对于广告转换测量用例，一方持有的标识符对应于看过广告活动的用户，而另一方持有的标识符和整数值分别对应于购买相关物品的用户和他们花费的金额。虽然广告转换问题是一个可以用私有交叉和协议解决的例子场景，但这个功能的适用范围更广。它可以很容易地扩展到其他统计数据，如平均值和方差。更广泛地说，PSI-Sum协议提供了一个安全的解决方案，适用于任何一方持有关于用户的私人统计数据，另一方持有关于特定人群中的用户成员的私人知识，并且双方都想了解该特定人群的总体统计数据的情况。例如，人们可以回答这样的问题："服用特定药物的病人的平均血压是多少？"或 "居住在特定邮政编码的人的住房拥有率是多少？"。

**贡献**：我们的贡献有两个方面。首先，我们详细描述了我们的部署，包括我们选择解决方案的约束和限制因素。这包括讨论安全聚合广告转换业务问题的特点，使其成为基于加密的MPC解决方案的良好候选。这些因素包括隐私需求和强大的商业利益，但也包括使用有效技术的问题的可操作性。该解决方案的关键制约因素是简单性和可解释性，以及易于实施、易于维护和可扩展性。

我们讨论了我们部署的协议的细节，该协议基于[41]的经典集合交叉协议，该协议使用Pohlig-Hellman密码（基于Decisional Diffie-Hellman（DDH）的难度）--该功能也可以被视为具有共享密钥的不经意PRF[34]。聚合属性是通过使用加法同态加密实现的。我们描述了典型的日常工作负载，以及运行这些工作负载的成本，包括货币成本。我们观察到，我们的应用不是实时的，可以使用廉价的低优先级的、可抢占的计算。在这种 "批量计算 "的环境中，带宽仍然是一种稀缺的共享资源，多个应用程序都在竞争（各种云供应商的资源价格见表1）。因此，通信复杂度成为我们协议最相关的效率衡量标准。我们相信，我们的见解对那些试图将安全计算技术用于实践的人来说是有用的。

作为我们的第二个主要贡献，我们通过最近大量改善高效PSI协议现状的论文[11], [31], [37], [47], [49], [51], [55]的视角，重新审视了具有Cardinality的隐私集合交点求和问题，以便将潜在的新解决方案的效率成本与我们部署的实现中使用的DDH风格协议进行比较。 我们的目标是看更多的现代技术是否能以增加复杂性为代价导致显著的节省。为此，我们将成本与最近的一套基于混淆电路式的技术[11]、[31]、[32]、[51]进行比较，这些技术明确考虑了交点上的隐私计算功能，并且可以直接扩展到计算我们的功能。我们还研究了最近计算隐私集合交集的方法[17], [20], [22], [37], [47], [49], 并试图使它们适应于计算具有Cardinality的隐私集合交点求和。

虽然最初的具有Cardinality的隐私集合交点求和功能看起来非常接近PSI功能，它安全地计算两个输入集的交集，但事实证明，在隐藏交集的同时实现额外的聚合是有效率成本的。同时，PSI功能是扩展功能的安全协议中的一个隐含的必要构件。因此，最近的PSI方法[17]、[20]、[22]、[37]、[47]、[49]需要明显不同的技术，以适应有cardinality的PSI-Sum设置。我们将调整工作集中在这些工作中的两个主要方法上。第一种是基于随机不经意传输，并建立在[49]和[37]所开发的技术上。这种方法利用了不经意PRF技术（OPRF），我们在两步不经意评估中对其进行了扩展，允许对评估的输入进行秘密置换。这使我们能够隐藏交集中的元素的身份。为了促进聚合功能，我们利用了加法同态加密，正如我们部署的协议一样。第二个协议是基于加密布隆过滤器的，并受到最近几个PSI解决方案的启发[17]、[20]、[22]。我们构建了一个不经意协议，用于在加性同态加密下评估加密布隆过滤器的成员资格。我们还使用加性同态加密来实现聚合功能。除了这两个新的构造，我们还给出了一个配方，用于将一个普通形式的PSI协议转换为计算具有Cardinality的隐私集合交点求和的协议。我们称这个配方为 "标签、洗牌、聚合"，并认为它适用于一类广泛的较新的方法。

此外，在我们上面总结的两个新的隐私集合交点求和协议，以及我们部署的协议中，输出接收方是拥有输入标识符和值对的一方。我们还构建了协议的 "反向 "变体，将输出接收方改为只有标识符的输入集的一方。我们所有的构造都实现了安全的计算功能，并对半诚实的对手具有安全性。

所有三个协议都使用加法同态加密（HE）作为构建模块。虽然我们部署的实现使用了Paillier[46]加密，并由于Damgard-Jurik[16]的优化，这在当时提供了最好的效率保证，但最近基于格子的构造的效率有了很大的提高[8]、[9]、[24]、[29]。我们将这两种方案与现有的第三种加法同态加密方案ElGamal[23]一起考虑，以进行综合比较，并分析我们的协议在与每个加法HE方案实例化时的效率权衡。

我们实现了我们所描述的每一个协议，并对它们在计算、通信和货币成本方面的性能进行了比较，同时也与最近使用混淆电路式技术对两个数据集的交集进行通用计算的协议进行了比较[11]、[31]、[50]。我们发现，在这些协议中，使用Paillier作为同态加密的DDH式协议实现了最低的货币成本，在10万个元素的输入集上需要0.084美分（USD）。我们还发现，我们针对PI-Sum的DDHstyle协议的变体，使用RLWE同态加密的关联值，在大小为100,000的集合上花费的时间少了约40%（47.4秒对74.4秒），货币成本减少了11%，为0.075美分。此外，我们所有的协议（DDH、ROT和Bloom Filter）在货币成本方面都超过了[11]和[31]的通用方法。[50]的方法优于我们基于布隆过滤器的解决方案，但在货币成本上比基于ROT和DDH的解决方案更昂贵。总的来说，在我们已经确定的限制条件下，部署的DDH协议仍然是我们的最佳选择。具体来说，基于部署的DDH协议的货币成本比任何基于混淆电路的新型通用方法都要便宜20倍。

**路线图**：在第2节中，我们详细讨论了我们问题的实际设置。在第3节中，我们给出了我们所部署的协议的细节。在第4节中，我们根据PSI的最新进展，重新审视了具有Cardinality的隐私集合交点求和问题。我们概述了最近的PSI方法，并在第4.2节中提出了将PSI协议转化为具有Cardinality的隐私集合交点求和的秘诀。在第4.3节中，我们提出了两个使用新技术的新构造。我们所有的构造都使用了附录A中定义的几个加密基元。在第5节中，我们介绍了我们的协议实现的测量结果，包括基于货币成本与基于混淆电路技术的工作进行比较。在附录A中，我们给出了各种有用的符号和定义。在附录B中，我们讨论了使用不同加密方案来实例化我们的协议的权衡。

## 2 问题的设定

我们现在描述问题的细节和我们的部署环境，包括正式的问题陈述和它的特点，我们的执行环境和日常工作负载的估计，以及我们用于协议的货币成本模型。

### 2.1 正式的问题陈述

在图1中，我们给出了一个关于我们旨在安全计算的功能的正式描述。在附录G中，我们还描述了一个反向的变体，即P1代替P2学习交集和S。我们的部署还假设双方已经拥有相同标识符空间的数据。找到一个适当的共同标识符空间是一个重要的问题，与当前的工作正交。

……

### 2.2 问题特征和制约因素

在这一节中，我们讨论了我们的部署所解决的业务问题的各种特征，即计算广告转化率指标。我们首先考虑使该问题适合于安全计算解决方案的特点。

……

### 2.3 对抗模型

另一个重要的设计轴是安全计算应该保护哪一类恶意行为。

我们可以用各种不同的模型来设计我们的协议，其中两个极端是完全信任和恶意对手模型。完全信任意味着各方相信对方会在明确的情况下正确计算数据，并在协议结束后删除数据。另一方面，恶意对手被允许任意地偏离任何规定的协议。在这两个极端之间存在中间概念，其中一个重要的概念是针对诚实但好奇的对手的安全性。提供 "诚实可信"（或半诚实）安全的协议，（在[58]中建模）假定参与者将诚实地遵循协议步骤，但可能试图从各种协议消息的记录本和日志中尽可能多地了解。

虽然对更强大的对手的保护自然更有吸引力，但它确实伴随着大量的效率成本（尤其是通信）。此外，加密协议的安全模型是全面风险分析的一部分，其中包括各方偏离的动机、基础数据的性质、互动各方之间的信任规模和水平，以及外部执行机制的可用性，如合同或代码审计。与恶意安全模型的协议相比，半诚实模型有相对有效的解决方案可用，特别是在通信成本和货币成本方面。它也是对完全信任模型的重大改进，该模型依靠外部非加密机制来确保隐私。特别是，半诚实模型对任何一方的数据泄露都给予了强有力的隐私保护，因为，由于半诚实的协议日志在规定的协议输出之外没有任何泄露。

在我们的部署中，考虑到所有因素，我们选择了 "半诚实 "的安全目标。

### 2.4 工作负载和执行环境

我们部署的一个典型的日常工作负载涉及每对当事人之间约1000个协议的执行，每个执行涉及每方输入中的100，000个项目。

我们的应用不是实时的，因此我们的部署环境是对延迟不敏感的批量计算的代表。每一方都控制着自己的计算和存储资源，此外，双方都可以访问共享的存储资源，用于传输协议执行的中间步骤的数据。1000个协议执行中的每一个都在共享存储中被分配了一个单独的目录。每当一方完成了某一特定执行的回合，它就将回合结果写入该执行的共享目录中。每一方都以相对较长的延迟（几分钟左右）不断轮询共享存储中的这些目录，以检查是否有新的文件被写入，如果有，就执行相应协议的下一轮执行。执行以这种方式继续，直到所有的执行都完成。

各方在他们自己的数据中心执行他们的协议部分。中间协议数据在这些数据中心之间使用互联网上的标准SSL连接进行传输。

### 2.5 货币成本模型

我们使用协议执行的总货币成本作为我们的主要成本指标。

……

### 2.6 相关工作

在实践中部署安全计算是具有挑战性的，但也有一些现实世界的应用利用了MPC。其中包括丹麦的甜菜拍卖[6]、爱沙尼亚的一个金融应用[5]、马萨诸塞州大学教师工资的安全调查[39]，以及一个报告骚扰行为的平台[54]。最近，Lindell等人[2]，[28]为在单一组织拥有的机器之间运行的加密操作部署了安全计算。谷歌也报告了使用安全计算协议来聚合来自移动设备的本地训练的机器学习模型[7]。然而，组织在多个实体或企业之间常规使用安全计算的情况仍然很少。

## 3 已部署的协议

在本节中，我们描述了我们部署的协议，即基于DDH的协议。

### 3.1 协议细节

在这里，我们提出了我们的基于DDH的相交和协议，这是我们针对上述限制条件而设计的。根据我们的理解，我们的协议是解决相交和问题的最简单的协议。它使用了众所周知的基于经典假设的加密基元，并可以从广泛部署的库（如OpenSSL）中构建。它的目标是半诚实的安全，并旨在最大限度地减少通信成本。此外，它足够灵活，允许几个重要的变体。

……

### 3.2 参数选择

在我们的部署中，我们使用OpenSSL的实现 "prime256v1"，一个具有256位群元素的NIST椭圆曲线，作为群G。对于随机神谕，我们使用SHA-256应用于输入，并重新应用，直到产生的输出位于椭圆曲线3上。为了在每次执行时模拟一个新的随机神谕，双方选择一个共同的随机种子，并在散列前将其预加到每个输入中。

对于加法同态加密方案，我们使用768位素数的Paillier加密，采用Damgard-Jurik优化[16]，s=3。因此，每个密码文本为6144位，明文空间为4608位。我们假设每个相关的整数值最多为32位，包括求和之后，因此我们可以将许多值打包到一个密码文本中。开槽的细节可以在附录B.1中看到。在槽之间允许40位的屏蔽，并留出一半的明文空间以允许槽被移位和添加，我们可以将65个整数值打包到一个密码文中。我们的Paillier实现是建立在OpenSSL的BigNum库之上的。

### 3.3 部署成本

在表2中，我们给出了单次会话的通信和计算成本，其中每一方的数据库中有100,000个条目，以及1000次这样的会议，这大致相当于一天的工作量。此外，我们使用表1中给出的GCP的资源估值给出了美元成本。运行时间是双方的总和，是在一台配备英特尔至强CPU E5-1650 v3（3.50 GHz）的台式工作站的单核上测量的，这在我们的部署中是典型的机器，也是谷歌云平台的虚拟CPU的代表。

我们看到，尽管原始计算时间似乎相当大，而通信相对适中，但通信的成本要比美元成本高3倍，占协议货币成本的75%。

### 3.4 变体

我们考虑了该协议在不同背景下的变体。这些变体对功能进行了修改，提供了重要的灵活性。

……

## 4 重新审视这个问题：新协议

在这一节中，我们转向这项工作的第二个主要贡献，即根据PSI协议的大量最新进展，重新审视安全计算私有交集-和-基数的问题。我们给出了两个基于新方法的新协议。此外，我们描述了一个简单的配方，将PSI协议的一个特别常见的味道变成一个具有Cardinality的隐私集合交点求和协议。

### 4.1 隐私集合求交集：概述

在一长串的工作中[14]、[15]、[17]、[20]、[22]、[26]、[32]、[33]、[37]、[38]、[49]、[52]、[55]、[56]已经广泛地研究了私有集相交。有几项工作将各方限制在只学习交集的cardinality [1], [13], [26], [33], [36], [44], [57] 。

……

### 4.2 将PSI转化为PIS：标签、洗牌和聚合

正如介绍中所讨论的，私有相交和的问题可以被看作是私有集合相交功能的扩展，此外，PSI功能是我们功能的一个隐含组成部分。因此，我们构造的自然起点是现有的PSI协议（我们部署的协议和我们的新构造都是如此）。我们从隐私集合求交集(PSI)到隐私集合交点求和(PIS)的高级秘诀如下：

……

### 4.3 具有Cardinality的隐私集合交点求和的新协议

在这一节中，我们介绍了我们的新加密协议，用于具有Cardinality的隐私集合交点求和，它利用了最近的ROT和BF技术，用于集合相交。

#### 4.3.1 基于随机OT的协议

在这一节中，我们描述了一个基于随机OT的相交和协议，它被用于现有的PSI解决方案中[20], [49], [52], [55]。我们认为这是第一个从随机OT中构建的具有Cardinality的隐私集合交点求和功能。请注意，我们的构造可以自然地修改为隐私计算PSI-cardinality的协议。

……

#### 4.3.2 基于布隆过滤器的协议

在本节中，我们描述了一个基于使用加密布隆过滤器的隐私集合交点求和协议，扩展了PSI方法[17]、[20]、[22]。

……

## 5 测量

在这一节中，我们介绍了第4.3.1节和第4.3.2节中介绍的我们的两个新的私有交集-和-cardinality协议的实现的测量结果，以及第3.1节中描述的我们部署的协议的额外测量结果，包括部署的协议和使用不同同态加密方案的变体。我们还将具体的成本与之前报道的基于乱码电路的方案的数字进行比较，特别是作品[31]、[49]、[50]、[52]，它们是在隐私交集上计算功能的最知名的作品。我们的比较包括基于 "批量计算 "场景的货币成本，使用表1中资源成本的GCP云定价。

在表3和表4中，我们以不同类型的操作和不同类型的传输元素的数量来表示每个协议的渐近成本。根据这些数字，我们预计DDH协议将有最好的通信，而在计算方面最有效的协议将取决于指数化和同态操作的相对成本，这一点我们通过实验来研究。

### 5.1 参数和加密方案

我们协议的所有计算成本测量都是以双方的总壁钟运行时间为基础的，运行在一台具有英特尔至强CPU E5-1650 v3（3.50 GHz）和32GB内存的台式工作站的单线程上，这与我们部署环境中的机器类似。计算成本不包括各方之间通过网络传输文件的时间。

对于所有的方案和数据库规模，我们假设输入域是128位字符串的集合，相关值最多为32位。我们还认为关联值的总和是以32比特为界限的。所有的计算成本都是假设每一方的输入中的每个条目都在集合的交集中（在所有协议中，这使计算量最大化）。

现在我们描述一下每个协议的加密方案和参数的选择。

……

### 5.2 测量的讨论

我们在表5中介绍了我们的测量结果，并在表6中介绍了货币成本。我们显示了基于DDH的已部署协议以及基于ROT和BF的两个新协议的成本，使用RLWE作为相关值的同态加密方案，还比较了我们的已部署协议，它使用DDH协议和Slotted Paillier作为加密方案（见第3.2节）。

我们看到，货币成本密切跟踪通信成本。使用Paillier的DDH协议具有最简洁的通信，也是最有效的货币成本，而ROT协议的货币成本和通信成本都要高出15倍，而基于BF的协议则要高出100倍。DDH协议，特别是用RLWE作为同态加密，被证明是我们计算效率最高的协议，比ROT和BF协议分别快25倍和40倍。最后，采用RLWE的DDH协议的货币成本比采用Paillier的DDH协议小11%，计算量减少约40%。

### 5.3 与混淆电路作品的比较

在本节中，我们将具体的成本（计算、通信和货币）与现有的基于乱码电路的工作中提出的成本进行比较，特别是[31]、[49]、[50]、[52]。对于这些成本，我们在很大程度上依赖于[50]的出色阐述，大量借鉴了[50]的表3和表5。

对于所有的Garbled Circuit协议，我们假设每一方的输入中的标识符被散列成 $40+\log(n)$ 比特长，其中n是输入大小：这可以防止除概率 $2^{-40}$ 以外的散列碰撞。

表7中列出了通信、计算和货币成本的比较。

我们注意到，由于几个原因，这些比较是不完美的。其中重要的一点是，[50]中提出的运行时间包括在局域网上的通信传输时间，而对于我们的协议，我们忽略了通信的时间，只包括计算的运行时间。这意味着我们在某种程度上高估了乱码电路式解决方案的计算成本。此外，测量使用的执行环境略有不同。另一点是，[50]中的乱码电路式解决方案的通信成本只是针对PSI功能，而不是针对私有交叉和。我们忽略了与计算相交和有关的额外成本，因此在某种程度上低估了Garbled-Circuit式解决方案的通信成本。

即使有这些注意事项，我们相信这个比较是有参考价值的，并且证明了我们的预期，即Garbled Circuit解决方案在计算上比我们提出的解决方案更快，但也产生了明显的通信成本。由于通信成本的巨大差异，在我们的成本模型中，这些协议的货币成本也要昂贵得多。

表7显示，基于ROT的协议和基于DDH的协议的两个变体，包括部署的协议，在货币方面比任何基于乱码电路的协议都要便宜。特别是，对于所考虑的数据大小，部署的协议比基于乱码电路的最便宜的协议[50]便宜20-30倍。我们基于布隆转换器的新协议也比除[50]之外的所有基于乱码电路的解决方案更便宜。

在本文新提出的协议中，就货币成本而言，基于DH的协议仍然是最便宜的。使用Paillier的DH协议（也就是我们部署的协议）在货币成本上比基于RLWE的变体要贵，但差别很小（大约10%）。同时，基于RLWE的协议在计算上要便宜40%。这意味着基于RLWE的协议在计算成本较高或通信成本比我们考虑的估值便宜的情况下可能特别有用。

## 6 总结

我们描述了在一个行业环境中部署一个安全的计算协议，作为不同公司之间业务互动的解决方案。我们的工作所解决的问题是保护隐私的综合广告转换的归属。我们描述了我们认为使这个问题很适合安全计算解决方案的因素，并描述了我们设计上的各种实际限制。

我们所部署的协议之所以被选中，是因为它的简单性，同时也是因为它的通信效率，这对货币成本有很大的影响。我们还根据最近的进展，重新审视了私人有底线的相交和问题，在此基础上我们构建了两个新的协议。我们实现了所有的构建，以评估和比较它们的具体成本，包括货币成本。从我们的测量结果来看，除了一个协议外，所有协议在货币成本方面与安全计算交集上的通用函数的方法相比都很好。我们部署的协议被发现在货币成本方面比通用方法便宜20倍。我们的其他解决方案提供了更好的计算，以换取通信。

## 参考文献

[1] Agrawal, R., Evfimievski, A.V., Srikant, R.: Information sharing across private databases. In: SIGMOD Conference. pp. 86–97. ACM (2003) 

[2] Araki, T., Furukawa, J., Lindell, Y., Nof, A., Ohara, K.: Highthroughput semi-honest secure three-party computation with an honest majority. In: ACM Conference on Computer and Communications Security. pp. 805–817. ACM (2016) 

[3] Bellare, M., Rogaway, P.: Random oracles are practical: A paradigm for designing efficient protocols. In: ACM Conference on Computer and Communications Security. pp. 62–73. ACM (1993) 

[4] Bloom, B.H.: Space/time trade-offs in hash coding with allowable errors. Communications of the ACM 13(7), 422–426 (1970) 

[5] Bogdanov, D., Talviste, R., Willemson, J.: Deploying secure multiparty computation for financial data analysis - (short paper). In: Financial Cryptography. Lecture Notes in Computer Science, vol. 7397, pp. 57–64. Springer (2012) 

[6] Bogetoft, P., Christensen, D.L., Damg ̊ ard, I., Geisler, M., Jakobsen, T.P., Krøigaard, M., Nielsen, J.D., Nielsen, J.B., Nielsen, K., Pagter, J., Schwartzbach, M.I., Toft, T.: Secure multiparty computation goes live. In: Financial Cryptography. Lecture Notes in Computer Science, vol. 5628, pp. 325–343. Springer (2009) 

[7] Bonawitz, K., Ivanov, V., Kreuter, B., Marcedone, A., McMahan, H.B., Patel, S., Ramage, D., Segal, A., Seth, K.: Practical secure aggregation for privacy-preserving machine learning. In: Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security. pp. 1175–1191. ACM (2017) 

[8] Brakerski, Z., Gentry, C., Vaikuntanathan, V.: (leveled) fully homomorphic encryption without bootstrapping. TOCT 6(3), 13:1–13:36 (2014) 

[9] Brakerski, Z., Vaikuntanathan, V.: Efficient fully homomorphic encryption from (standard) LWE. SIAM J. Comput. 43(2), 831871 (2014) 

[10] Chen, H., Laine, K., Rindal, P.: Fast private set intersection from homomorphic encryption. In: ACM Conference on Computer and Communications Security. pp. 1243–1255. ACM (2017) 

[11] Ciampi, M., Orlandi, C.: Combining private set-intersection with secure two-party computation. In: International Conference on Security and Cryptography for Networks. pp. 464–482. Springer (2018) 

[12] Corrigan-Gibbs, H., Boneh, D.: Prio: Private, robust, and scalable computation of aggregate statistics. In: 14th USENIX Symposium on Networked Systems Design and Implementation (NSDI 17). pp. 259–282 (2017) 

[13] Cristofaro, E.D., Gasti, P., Tsudik, G.: Fast and private computation of cardinality of set intersection and union. In: CANS. vol. 7712, pp. 218–231. Springer (2012) 

[14] Cristofaro, E.D., Kim, J., Tsudik, G.: Linear-complexity private set intersection protocols secure in malicious model. In: ASIACRYPT. Lecture Notes in Computer Science, vol. 6477, pp. 213–231. Springer (2010) 

[15] Dachman-Soled, D., Malkin, T., Raykova, M., Yung, M.: Efficient robust private set intersection. In: International Conference on Applied Cryptography and Network Security. pp. 125–142. Springer (2009) 

[16] Damg ̊ ard, I., Jurik, M.: A generalisation, a simplification and some applications of Paillier’s probabilistic public-key system. In: Public Key Cryptography. Lecture Notes in Computer Science, vol. 1992, pp. 119–136. Springer (2001) 

[17] Debnath, S.K., Dutta, R.: Secure and efficient private set intersection cardinality using bloom filter. In: International Information Security Conference. pp. 209–226. Springer (2015) 

[18] Demmler, D., Rindal, P., Rosulek, M., Trieu, N.: Pir-psi: scaling private contact discovery. Proceedings on Privacy Enhancing Technologies 2018(4), 159–178 (2018) 

[19] Diffie, W., Hellman, M.: New directions in cryptography. IEEE transactions on Information Theory 22(6), 644–654 (1976)

[20] Dong, C., Chen, L., Wen, Z.: When private set intersection meets big data: an efficient and scalable protocol. In: Proceedings of the 2013 ACM SIGSAC conference on Computer & communications security. pp. 789–800. ACM (2013) 

[21] Dwork, C., McSherry, F., Nissim, K., Smith, A.: Calibrating noise to sensitivity in private data analysis. In: Theory of Cryptography (2006) 

[22] Egert, R., Fischlin, M., Gens, D., Jacob, S., Senker, M., Tillmanns, J.: Privately computing set-union and set-intersection cardinality via bloom filters. In: Australasian Conference on Information Security and Privacy. pp. 413–430. Springer (2015) 

[23] ElGamal, T.: A public key cryptosystem and a signature scheme based on discrete logarithms. IEEE transactions on information theory 31(4), 469–472 (1985) 

[24] Fan, J., Vercauteren, F.: Somewhat practical fully homomorphic encryption. IACR Cryptology ePrint Archive 2012, 144 (2012) 

[25] Freedman, M.J., Ishai, Y., Pinkas, B., Reingold, O.: Keyword search and oblivious pseudorandom functions. In: Theory of Cryptography Conference. pp. 303–324. Springer (2005) 

[26] Freedman, M.J., Nissim, K., Pinkas, B.: Efficient private matching and set intersection. In: International conference on the theory and applications of cryptographic techniques. pp. 1–19. Springer (2004) 

[27] Froelicher, D., Egger, P., Sousa, J.S., Raisaro, J.L., Huang, Z., Mouchet, C., Ford, B., Hubaux, J.P.: Unlynx: a decentralized system for privacy-conscious data sharing. Proceedings on Privacy Enhancing Technologies 2017(4), 232–250 (2017) 

[28] Furukawa, J., Lindell, Y., Nof, A., Weinstein, O.: High-throughput secure three-party computation for malicious adversaries and an honest majority (2017) 

[29] Gentry, C., Halevi, S., Smart, N.P.: Fully homomorphic encryption with polylog overhead. In: Annual International Conference on the Theory and Applications of Cryptographic Techniques. pp. 465482. Springer (2012) 

[30] Hellman, M.E., Pohlig, S.C.: Exponentiation cryptographic apparatus and method (Jan 3 1984), uS Patent 4,424,414 

[31] Hemenway Falk, B., Noble, D., Ostrovsky, R.: Private set intersection with linear communication from general assumptions. In: Proceedings of the 18th ACM Workshop on Privacy in the Electronic Society. pp. 14–25 (2019) 

[32] Huang, Y., Evans, D., Katz, J.: Private set intersection: Are garbled circuits better than custom protocols? In: NDSS (2012) 

[33] Huberman, B.A., Franklin, M., Hogg, T.: Enhancing privacy and trust in electronic communities. In: Proceedings of the 1st ACM conference on Electronic commerce. pp. 78–86. ACM (1999) 

[34] Jarecki, S., Liu, X.: Fast secure computation of set intersection. In: SCN. Lecture Notes in Computer Science, vol. 6280, pp. 418–435. Springer (2010) 

[35] Kiss,  ́ A., Liu, J., Schneider, T., Asokan, N., Pinkas, B.: Private set intersection for unequal set sizes with mobile applications. Proceedings on Privacy Enhancing Technologies 2017(4), 177–197 (2017) 

[36] Kissner, L., Song, D.: Privacy-preserving set operations. In: Proceedings of the 25th Annual International Conference on Advances in Cryptology. pp. 241–257. CRYPTO’05, Springer-Verlag, Berlin, Heidelberg (2005), http://dx.doi.org/10.1007/11535218 15 

[37] Kolesnikov, V., Kumaresan, R., Rosulek, M., Trieu, N.: Efficient batched oblivious prf with applications to private set intersection. In: Proceedings of the 2016 ACM SIGSAC Conference on Computer and Communications Security. pp. 818–829. ACM (2016) 

[38] Lambæk, M.: Breaking and fixing private set intersection protocols. Tech. rep., Cryptology ePrint Archive, Report 2016/665, 2016. http://eprint. iacr. org/2016/665 (2016) 

[39] Lapets, A., Volgushev, N., Bestavros, A., Jansen, F., Varia, M.: Secure multi-party computation for analytics deployed as a lightweight web application. Tech. rep., Computer Science Department, Boston University (2016) 

[40] Le, P.H., Ranellucci, S., Gordon, S.D.: Two-party private set intersection with an untrusted third party. In: Proceedings of the 2019 ACM SIGSAC Conference on Computer and Communications Security. pp. 2403–2420. ACM (2019)

[41] Meadows, C.: A more efficient cryptographic matchmaking protocol for use in the absence of a continuously available third party. In: Security and Privacy, 1986 IEEE Symposium on. pp. 134–134. IEEE (1986) 

[42] Mitzenmacher, M., Upfal, E.: Probability and computing: Randomized algorithms and probabilistic analysis. Cambridge university press (2005) 

[43] Naor, M., Reingold, O.: Number-theoretic constructions of efficient pseudo-random functions. J. ACM 51(2), 231–262 (2004) 

[44] Narayanan, G.S., Aishwarya, T., Agrawal, A., Patra, A., Choudhary, A., Rangan, C.P.: Multi party distributed private matching, set disjointness and cardinality of set intersection with information theoretic security. In: International Conference on Cryptology and Network Security. pp. 21–40. Springer (2009) 

[45] Pagh, R., Rodler, F.F.: Cuckoo hashing. J. Algorithms 51(2), 122144 (2004) 

[46] Paillier, P.: Public-key cryptosystems based on composite degree residuosity classes. In: International Conference on the Theory and Applications of Cryptographic Techniques. pp. 223–238. Springer (1999) 

[47] Pinkas, B., Rosulek, M., Trieu, N., Yanai, A.: SpOT-light: Lightweight private set intersection from sparse OT extension. In: CRYPTO (3). Lecture Notes in Computer Science, vol. 11694, pp. 401–431. Springer (2019) 

[48] Pinkas, B., Rosulek, M., Trieu, N., Yanai, A.: Spot-light: Lightweight private set intersection from sparse ot extension. In: Annual International Cryptology Conference. pp. 401–431. Springer (2019) 

[49] Pinkas, B., Schneider, T., Segev, G., Zohner, M.: Phasing: private set intersection using permutation-based hashing. In: Proceedings of the 24th USENIX Conference on Security Symposium. pp. 515530. USENIX Association (2015) 

[50] Pinkas, B., Schneider, T., Tkachenko, O., Yanai, A.: Efficient circuit-based PSI with linear communication. In: EUROCRYPT (3). Lecture Notes in Computer Science, vol. 11478, pp. 122–153. Springer (2019) 

[51] Pinkas, B., Schneider, T., Weinert, C., Wieder, U.: Efficient circuitbased psi via cuckoo hashing. In: Annual International Conference on the Theory and Applications of Cryptographic Techniques. pp. 125–157. Springer (2018) 

[52] Pinkas, B., Schneider, T., Zohner, M.: Faster private set intersection based on ot extension. In: Usenix Security. vol. 14, pp. 797–812 (2014) 

[53] Pinkas, B., Schneider, T., Zohner, M.: Scalable private set intersection based on OT extension. ACM Trans. Priv. Secur. 21(2), 7:1–7:35 (2018) 

[54] Rajan, A., Qin, L., Archer, D.W., Boneh, D., Lepoint, T., Varia, M.: Callisto: A cryptographic approach to detecting serial perpetrators of sexual misconduct. In: COMPASS. pp. 49:1–49:4. ACM (2018) 

[55] Rindal, P., Rosulek, M.: Improved private set intersection against malicious adversaries. Tech. rep. (2016) 

[56] Segal, A., Ford, B., Feigenbaum, J.: Catching bandits and only bandits: Privacy-preserving intersection warrants for lawful surveillance. In: FOCI (2014) 

[57] Vaidya, J., Clifton, C.: Secure set intersection cardinality with application to association rule mining. Journal of Computer Security 13(4), 593–622 (2005) 

[58] Yao, A.C.C.: How to generate and exchange secrets. In: 27th Annual Symposium on Foundations of Computer Science (sfcs 1986). pp. 162–167. IEEE (1986)

## 附录A 前言、密码学原理和难度假设

### A.1 符号

……

### A.2 决策性 Diffie-Hellman

……

### A.3 随机预言模型

……

### A.4 加法同态加密方案

……

### A.5 不经意伪随机函数（OPRF）

……

### A.6 随机不经意传输 (ROT)

……

### A.7 布隆过滤器

……

### A.8 布谷鸟哈希

……

## 附录B 同态加密方案的实例化

我们提出的三个私人相交和协议中的每一个都需要一个加法同态加密方案，以便对相关的值进行加密并对它们进行同态求和。基于Random-OT的协议和基于Bloom-filter的协议还依赖于一个加法同态加密方案，以便对标识符本身进行加密和相交。同态加密方案的选择对每个协议的通信和计算成本都有很大影响。在本节中，我们讨论了我们可以使用的三种可能的加法同态加密方案，即Paillier加密[46]、指数ElGamal加密[23]和基于Ring-WE的方案[8]、[9]、[24]、[29]。我们讨论了每种方案的各种特点，以及可以应用于每种方案的优化。这些差异在图5中进行了总结。

### B.1 Paillier加密

……

### B.2 指数ElGamal

……

### B.3 基于环容错学习问题的密码系统

……

## 附录C 基于混淆电路式方法的分析比较

……

## 附录D 基于DDH协议的安全分析

……

## 附录E 基于随机OT的协议的安全分析

……

## 附录F 基于Bloom-Filter的协议的安全分析

……

## 附录G "反向 "变体

……

### G.1 基于DDH的 "反向 "协议

……

### G.2 安全分析

……

## 附录H 额外的测量

### H.1 使用一个理想化的同态加密方案

……

### H.2 为基于随机OT的协议使用不同的加法加密方案

……