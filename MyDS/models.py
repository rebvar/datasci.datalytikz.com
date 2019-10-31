from app import db



class User(db.Model):

    """
    The user table. Holds the login information. Is used to keep track of different users' data and 
    experiments. 
    """

    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    name = db.Column(db.String)
    utype = db.Column(db.Integer, unique=False)
    
    af = db.Column(db.Integer, unique=False)
    registrationDate = db.Column(db.String)
    bs = db.Column(db.Integer, unique=False)
    profilePic = db.Column(db.String, default = '')

    experiments = db.relationship('Experiment', backref='User', lazy=True)
    blogPosts = db.relationship('BlogPost', backref='User', lazy=True)
    postLikes = db.relationship('PostLike', backref='User', lazy=True)
    commentVotes = db.relationship('CommentVote', backref='User', lazy=True)
    repos = db.relationship('Repo', backref='User', lazy=True)
    notifications = db.relationship('Notification', backref='User', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.username


class Notification (db.Model):
    """
    Notifications to logged on users regarding the status of their created jobs
    """

    __tablename__='Notification'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'),
        nullable=False)
    notText = db.Column(db.String)
    notType = db.Column(db.String)
    notSource = db.Column(db.String)
    observed = db.Column(db.Integer)
    notDate = db.Column(db.String)
    notViewDate = db.Column(db.String)
    



class Experiment(db.Model):

    """
    Experiment table holds the information for the designed models and their predictions. Initially,
    intended for the defect prediction models, but can be used for other experiments, filtered by the 
    type column. 
    Experiment parameters and the results are stored in json format, which makes the model flexible enough 
    for different types of experiments.
    """

    __tablename__='Experiment'
    id = db.Column(db.Integer, primary_key=True)
    results = db.Column(db.String)
    pars = db.Column(db.String)
    type = db.Column(db.String(200))
    startDateTime = db.Column(db.String(50))
    endDateTime = db.Column(db.String(50))
    userId = db.Column(db.Integer, db.ForeignKey('User.id'),
        nullable=False)
    expModelsFileName = db.Column(db.String)
    experimentPredictons = db.relationship('ExperimentPrediction', backref='Experiment', lazy=True)

class ExperimentPrediction(db.Model):
    """
    Output of prediction models that are generated from the experiments for predictive experiments.
    """


    __tablename__='ExperimentPrediction'
    id = db.Column(db.Integer, primary_key=True)
    expId = db.Column(db.Integer, db.ForeignKey('Experiment.id'),
        nullable=False)    
    datasetName = db.Column(db.String)
    predDateTime = db.Column(db.String(50))    
    predResult = db.Column(db.String)
    data = db.Column(db.String)
    predType = db.Column(db.Integer)


class BlogPost(db.Model):
    """
    As the name suggests, a post in the blog section
    """

    __tablename__ = 'BlogPost'
    id = db.Column(db.Integer, primary_key=True)
    postTitle = db.Column(db.String)
    postBody = db.Column(db.String)
    postDate = db.Column(db.String(50))
    postPerms = db.Column(db.Integer)
    viewCount = db.Column(db.Integer)
    postCreatorId = db.Column(db.Integer, db.ForeignKey('User.id'),
        nullable=False)

    postLikes = db.relationship('PostLike', backref='BlogPost', lazy=True)
    postComments = db.relationship('PostComment', backref='BlogPost', lazy=True)

class PostLike(db.Model):
    """
    Blog post likes by users
    """

    __tablename__ = 'PostLike'
    id = db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('BlogPost.id'),
        nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'),
        nullable=False)

class PostComment(db.Model):
    """
    Comments on the blog posts. 
    Track the parent comments using the inReplyTo column.
    """

    __tablename__ = 'PostComment'
    id =  db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('BlogPost.id'), nullable=False)
    commentText = db.Column(db.String)
    inReplyTo =  db.Column(db.Integer)        
    commentorId = db.Column(db.Integer)  
    commentorName = db.Column(db.String)
    commentorEmail = db.Column(db.String)
    commentDate = db.Column(db.String)
    commentVotes = db.relationship('CommentVote', backref='PostComment', lazy=True)

class CommentVote(db.Model):
    """
    Tracking the votes on comments in the blog per comment and per user. Only one up/down vote 
    is accepted by a user on a single comment.
    """

    __tablename__ = 'CommentVote'
    id = db.Column(db.Integer, primary_key=True)
    commentId = db.Column(db.Integer, db.ForeignKey('PostComment.id'),
        nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'),
        nullable=False)
    isUpVote = db.Column(db.Integer)

class Dataset(db.Model):
    """
    Unification of the utilized datasets. Keeping track of the different fields of the data. 
    Leverages reusability of data. 

    Planned: to be able to share the data with other users and publicly in future.
    """

    __tablename__='Dataset'    
    id = db.Column(db.Integer, primary_key=True)
    datasetName = db.Column(db.String)
    datasetGroupId = db.Column(db.Integer, db.ForeignKey('DatasetGroup.id'), nullable=False)
    numFeatures = db.Column(db.Integer)
    numInstances = db.Column(db.Integer)
    classType = db.Column(db.Integer)
    featuresList = db.Column(db.String)
    datasetFor = db.Column(db.String)
    data = db.Column(db.String)
    path = db.Column(db.String)

class DatasetGroup(db.Model):
    """
    Categorization of the datasets
    """
    __tablename__='DatasetGroup'    
    id = db.Column(db.Integer, primary_key=True)
    datasetGroupName = db.Column(db.String)
    datasetGroupCreator = db.Column(db.String)
    datasets = db.relationship('Dataset', backref='DatasetGroup', lazy=True)


class Repo(db.Model):

    """
    Cloned repositories. Initially planned for Github and Mercurial, but plan to implement support
    for any library that provide such capabilities. Hold repository info. Actual files of the 
    repository are hold separately on the disk and are used using appropriate libraries.
    """

    __tablename__ = 'Repo'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String)
    url = db.Column(db.String)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'),
        nullable=False)
    repoInfo = db.Column(db.String)
    cloneStartDate = db.Column(db.String)
    cloneFinishDate = db.Column(db.String)
    isPrivate = db.Column(db.Integer)
    repoName = db.Column(db.String)
    logs = db.relationship('Log', backref='Repo', lazy=True)
    repoFiles = db.relationship('RepoFile', backref='Repo', lazy='dynamic')
    revData = db.relationship('RevisionData', backref='Repo', lazy=True)
    szzBlames = db.relationship('SZZBlame', backref='Repo', lazy=True)

class Log(db.Model):

    """
    Holds cloned software repository logs. Initially planned for line of code origin tracking using
    SZZ for defect blaming.
    """

    __tablename__ = 'Log'
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.String)
    m = db.Column(db.String)
    author = db.Column(db.String)
    repoId = db.Column(db.Integer, db.ForeignKey('Repo.id'),
        nullable=False)
    parents = db.Column(db.String)
    date = db.Column(db.String)
    tags = db.Column(db.String)
    branches = db.Column(db.String)
    files = db.Column(db.String)
    timestamp = db.Column(db.String)
    pushdateTimestamp = db.Column(db.String)
    gDump = db.Column(db.String)

    revIndex = db.Column(db.Integer)    
    bugs = db.Column(db.String)    
    bugFixes = db.relationship('BugFix', backref='Log', lazy=True)

class RepoFile(db.Model):
    """
    Holds the information regarding the unique files in the cloned repositories. Currently, used 
    for defect blaming using SZZ.
    """

    __tablename__ = 'RepoFile'
    id = db.Column(db.Integer, primary_key=True)
    repoId = db.Column(db.Integer, db.ForeignKey('Repo.id'),
        nullable=False)
    file = db.Column(db.String)
    revs = db.Column(db.String)
    authors = db.Column(db.String)    
    revData = db.relationship('RevisionData', backref='RepoFile', lazy=True)

class RevisionData(db.Model):
    """
    Holds the revision data for a software repossitory changeset. Used for defect blaming
    based on SZZ.
    Plan to remove from the database and create local databases per SZZ repo.
    """

    __tablename__ = 'RevisionData'
    id = db.Column(db.Integer, primary_key=True)
    repoFileId = db.Column(db.Integer, db.ForeignKey('RepoFile.id'),
        nullable=False)
    repoId = db.Column(db.Integer, db.ForeignKey('Repo.id'),
        nullable=False)
    rev = db.Column(db.String)
    author = db.Column(db.String)
    revIndex = db.Column(db.Integer)
    gDump = db.Column(db.String)
    graphType = db.Column(db.Integer, default = 0)
    

class BugPattern(db.Model):

    """
    Regex patterns used for identifying bug-fixes in software changeset comments.
    """
    __tablename__='BugPattern'
    id = db.Column(db.Integer, primary_key=True)
    patternList = db.Column(db.String)
    bugFixes = db.relationship('BugFix', backref='BugPattern', lazy=True)

class BugFix (db.Model):
    """
    Identified bugs per bug pattern for a software repository log.
    """

    __tablename__='BugFix'
    id = db.Column(db.Integer, primary_key=True)
    bugPatternId = db.Column(db.Integer, db.ForeignKey('BugPattern.id'),
        nullable=False)
    bugs = db.Column(db.String)
    isBugFix = db.Column(db.Integer)
    logId = db.Column(db.Integer, db.ForeignKey('Log.id'),
        nullable=False)


class SZZBlame (db.Model):
    """
    Blaming information for SZZ.
    """

    __tablename__='SZZBlame'
    id = db.Column(db.Integer, primary_key=True)
    repoId = db.Column(db.Integer, db.ForeignKey('Repo.id'),
        nullable=False)
    blames = db.Column(db.String)
    blamesAnalysis = db.Column(db.String)
    szzType = db.Column(db.Integer)
    szzDesc = db.Column(db.String)

