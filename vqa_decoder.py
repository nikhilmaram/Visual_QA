import tensorflow as tf
import numpy as np

class vqa_decoder:
    def __init__(self,config):
        self.config =  config
        print("decoder model created")


    def build(self,image_features,question_features):

        print("Building Decoder")
        config = self.config
        self.is_train = config.PHASE
        self.image_features = image_features
        self.question_features = question_features

        # Setup the placeholders
        if self.is_train:
            # contexts = self.conv_feats
            self.answers = tf.placeholder(
                dtype=tf.int32,
                shape=[config.BATCH_SIZE, config.MAX_ANSWER_LENGTH])
            self.answer_masks = tf.placeholder(
                dtype=tf.float32,
                shape=[config.BATCH_SIZE, config.MAX_ANSWER_LENGTH])

        ## Point wise multiplication

        self.point_wise = tf.multiply(self.image_features,self.question_features)


        ## Build a Fully Connected Layer
        with tf.variable_scope('fc_decoder', reuse=tf.AUTO_REUSE) as scope:
            fcw = tf.get_variable(initializer=tf.truncated_normal([self.config.POINT_WISE_FEATURES, self.config.OUTPUT_SIZE],
                                                   dtype=tf.float32,
                                                   stddev=1e-1), name='fc_W',trainable=True)
            fcb = tf.get_variable(initializer=tf.constant(1.0, shape=[self.config.OUTPUT_SIZE], dtype=tf.float32),
                               trainable=True, name='fc_b')
            fcl = tf.nn.bias_add(tf.matmul(self.point_wise, fcw), fcb)
            logits = tf.nn.relu(fcl)

        if self.is_train:
            # Compute the loss for this step, if necessary
            # one_hot_encode_map = lambda x : self.onehot_encode(x)
            # one_hot_encoded_answer = tf.map_fn(one_hot_encode_map,self.answers.values)
            # cross_entropy_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            #     labels=self.onehot_encode(self.answers[:,0]), ##[:,0] because answers is array of arrays
            #     logits=logits)
            print("One hot encoding size : {}".format(tf.one_hot(self.answers[:,0], depth=self.config.TOP_ANSWERS).get_shape()))
            print("Logits size : {}".format(logits.get_shape()))
            cross_entropy_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                labels=self.answers[:,0],  ##[:,0] because answers is array of arrays
                logits=logits)

            self.optimizer = tf.train.AdamOptimizer(config.INITIAL_LEARNING_RATE).minimize(cross_entropy_loss)

        self.predictions = tf.argmax(logits, 1)
        print(" Decoder model built")


    def onehot_encode(self,answer):
        vector = np.zeros(self.config.TOP_ANSWERS)
        vector[int(answer)] = 1
        return vector
    # def onehot_encode(self,answers):
    #     onehot_vector = []
    #     for ans in answers:
    #         vector = np.zeros(self.config.TOP_ANSWERS)
    #         vector[int(ans)] = 1
    #         onehot_vector.append(vector)
    #     return np.array(onehot_vector)