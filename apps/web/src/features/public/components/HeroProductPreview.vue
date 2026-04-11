<template>
  <div class="hero-preview">
    <div class="hero-preview-window">
      <div class="hero-preview-bar">
        <span />
        <span />
        <span />
      </div>

      <div class="hero-preview-content">
        <aside class="hero-preview-sidebar">
          <div class="hero-preview-sidebar-title">备课台</div>
          <div class="hero-preview-sidebar-card active">
            <div class="hero-preview-label">数学 · 八年级</div>
            <div class="hero-preview-strong">一元二次方程</div>
          </div>
          <div class="hero-preview-sidebar-card">
            <div class="hero-preview-label">AI 生成中</div>
            <div class="hero-preview-muted">导入环节 / 练习巩固</div>
          </div>
        </aside>

        <section class="hero-preview-editor">
          <div class="hero-preview-editor-head">
            <div>
              <div class="hero-preview-label">编辑器</div>
              <div class="hero-preview-strong">10 分钟，搞定一份好教案</div>
            </div>
            <div class="hero-preview-export">导出 ▾</div>
          </div>

          <div class="hero-preview-section">
            <div class="hero-preview-section-title">教学目标</div>
            <div class="hero-preview-line long" />
            <div class="hero-preview-line medium" />
          </div>

          <div class="hero-preview-section pending">
            <div class="hero-preview-chip">AI 待确认</div>
            <div class="hero-preview-section-title">导入环节（5 分钟）</div>
            <div class="hero-preview-line long" />
            <div class="hero-preview-line medium" />
            <div class="hero-preview-actions">
              <span>接受</span>
              <span>拒绝</span>
              <span>重新生成</span>
            </div>
          </div>

          <div class="hero-preview-bottom">
            <span>开始备课</span>
            <span>AI 补充内容</span>
            <span>添加练习</span>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
